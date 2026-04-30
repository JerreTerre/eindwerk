from gpiozero import AngularServo
from time import sleep
from simple_pid import PID
from threading import Lock
import _thread
from flask import Flask, request, render_template
import busio
import board
import adafruit_bh1750
import pymysql
import paho.mqtt.client as mqtt

# =========================
# HARDWARE
# =========================


i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bh1750.BH1750(i2c)
servo = AngularServo(17, initial_angle=0, min_angle=180, max_angle=0, min_pulse_width=7/10000, max_pulse_width=25/10000)
servo.angle=0
# =========================
# VARIABELEN & PID
# =========================
lichtX = 0.0  # Gemeten temperatuur
W = 200     # Setpoint (Gewenste temp)
y = 0.0      # Stuurwaarde in %

P, I, D = 1.5, 0.1, 1
pid = PID(P, I, D, setpoint=W)
pid.sample_time = 0.1
pid.output_limits = (0, 100)

pid_lock = Lock()

# Database connectie
conn = pymysql.connect(
    host='127.0.0.1',
    unix_socket='/var/run/mysqld/mysqld.sock',
    user='Smets',
    passwd='Thomas',
    db='paasexaam'
)
cur = conn.cursor()




# =========================
# REGELTHREAD (Achtergrond)
# =========================
def regel_loop():
    global lichtX, y, W
    try:
        # lege tabel éénmalig bij opstart
        cur.execute("TRUNCATE TABLE waarden")
        conn.commit()

        while True:
            # 1. Meten
            lichtX=round(sensor.lux)
            print(lichtX)
            # 2. PID‑berekening
            with pid_lock:
                pid.setpoint = W
                y_raw = pid(lichtX)
                y = y_raw
            # 3. PWM uitsturen
            val = max(0, min(100, y))

            servo.angle = val

            # 4. Data opslaan – nu de werkelijke W, X en Y
            cur.execute("""
                INSERT INTO waarden (time, W, X, Y)
                VALUES (NOW(), %s, %s, %s)
            """, (W, lichtX, y))
            conn.commit()


            sleep(0.5)
    finally:
        servo.angle=0

# Start de regeling in een aparte thread
_thread.start_new_thread(regel_loop, ())

# =========================
# FLASK SERVER
# =========================
app = Flask(
    __name__,
    static_url_path="",
    static_folder="www",
    template_folder="www"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dataout1")
def dataout1():
    global lichtX, W, y
    return (
        f"<p>Werkelijke waarde (X): {lichtX} lux</p>"
        f"<p>Gewenste waarde (W): {W} lux</p>"
        f"<p>PWM: {y:.1f} %</p>"
    )

@app.route("/updateW", methods=["POST"])
def updateW():
    global W
    W = float(request.form["Wnew"])
    return ""

@app.route("/updatePID", methods=["POST"])
def updatePID():
    global P, I, D, pid
    P = float(request.form["P"])
    I = float(request.form["I"])
    D = float(request.form["D"])

    with pid_lock:
        pid.tunings = (P, I, D)
        pid.reset()
    return ""

@app.route("/pidvalues")
def pidvalues():
    return {"P": P, "I": I, "D": D}

@app.route("/values")
def values():
    print(lichtX)
    return {
        "X": lichtX,
        "W": W,
        "Y": round(y, 1)
    }

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5050,
        use_reloader=False
    )