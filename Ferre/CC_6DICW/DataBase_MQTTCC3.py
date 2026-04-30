from gpiozero import PWMLED
from time import sleep
from simple_pid import PID
from threading import Lock
import _thread
from flask import Flask, request, render_template
import busio
import board
import adafruit_bmp280
import pymysql
import paho.mqtt.client as mqtt

# =========================
# HARDWARE
# =========================
pwm_device = PWMLED(27)
pwm_device.value = 0

i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

# =========================
# VARIABELEN & PID
# =========================
tempX = 0.0  # Gemeten temperatuur
W = 35.0     # Setpoint (Gewenste temp)
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
    db='CC4'
)
cur = conn.cursor()

Wmqtt = 0.0
Xmqtt = 0.0
Ymqtt = 0.0

# =========================
# MQTT SETUP
# =========================
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Verbonden met MQTT broker")
        client.subscribe("W")
        client.subscribe("X")
        client.subscribe("Y")
    else:
        print(f"Verbinding mislukt, code: {reason_code}")

def on_message(client, userdata, msg):
    global Wmqtt, Xmqtt, Ymqtt
    payload = msg.payload.decode()
    
    try:
        val = round(float(payload), 1)
        if msg.topic == "W":
            Wmqtt = val
            print("W:", Wmqtt)
        elif msg.topic == "X":
            Xmqtt = val
            print("Temp:", Xmqtt)
        elif msg.topic == "Y":
            Ymqtt = val
            print("PWM:", Ymqtt)
    except ValueError:
        print("Foutieve payload ontvangen")

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    protocol=mqtt.MQTTv5
)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883)
client.loop_start()  # Draait op de achtergrond

# =========================
# REGELTHREAD (Achtergrond)
# =========================
def regel_loop():
    global tempX, y, W
    try:
        # lege tabel éénmalig bij opstart
        cur.execute("TRUNCATE TABLE waarde")
        conn.commit()

        while True:
            # 1. Meten
            tempX = round(bmp280.temperature, 1)

            # 2. PID‑berekening
            with pid_lock:
                pid.setpoint = W
                y_raw = pid(tempX)
                y = y_raw

            # 3. PWM uitsturen
            val = max(0, min(100, y))
            pwm_device.value = val / 100

            # 4. Data opslaan – nu de werkelijke W, X en Y
            cur.execute("""
                INSERT INTO waarde (time, W, X, Y)
                VALUES (NOW(), %s, %s, %s)
            """, (W, tempX, y))
            conn.commit()

            # 5. stuur de waardes over MQTT (we zijn ook op deze topics
            #    geabonneerd, dus we “subben naar onszelf”)
            client.publish("W", W)
            client.publish("X", tempX)
            client.publish("Y", y)

            sleep(0.5)
    finally:
        pwm_device.off()

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
    global tempX, W, y
    return (
        f"<p>Werkelijke waarde (X): {tempX} °C</p>"
        f"<p>Gewenste waarde (W): {W} °C</p>"
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
    return {
        "X": tempX,
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