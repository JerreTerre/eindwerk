# =========================
# LIBRARIES
# =========================
from gpiozero import PWMLED
from time import sleep
from simple_pid import PID
import os
from threading import Lock
import _thread
from flask import Flask, request, render_template
import busio
import board
import adafruit_bmp280

# =========================
# HARDWARE
# =========================
pwm_device = PWMLED(27)
pwm_device.value = 0

# I2C + BMP280 (Adafruit)
i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

# =========================
# VARIABELEN
# =========================
tempX = 0.0     # gemeten temperatuur
W = 24.0        # gewenste temperatuur
y = 0.0         # PWM stuurwaarde (%)

P = 2.0
I = 1.0
D = 0.5

pid_lock = Lock()

# =========================
# PID
# =========================
pid = PID(P, I, D, setpoint=W)
pid.sample_time = 0.1
pid.output_limits = (0, 100)
pid.auto_mode = True

# =========================
# REGELTHREAD
# =========================
def regel_loop():
    global tempX, y, W

    try:
        while True:
            os.system("clear")

            # Temperatuur meten
            tempX = round(bmp280.temperature, 1)

            # PID berekenen (THREAD-SAFE)
            with pid_lock:
                pid.setpoint = W
                y = pid(tempX)

            # Inverteren (airco-logica)
            y = 100 - y

            # Ventilator start pas vanaf 20%
            y = 20 + (y / 5 * 4)

            # Begrenzen
            y = max(0, min(100, y))

            # PWM uitsturen
            pwm_device.value = y / 100

            # Debug
            print(f"Temperatuur: {tempX} °C")
            print(f"Setpoint: {W} °C")
            print(f"PWM: {y:.1f} %")

            sleep(0.1)

    finally:
        pwm_device.off()
        print("Regeling gestopt")

# =========================
# START REGELTHREAD
# =========================
_thread.start_new_thread(regel_loop, ())

# =========================
# FLASK
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

# ===== SETPOINT SLIDER =====
@app.route("/updateW", methods=["POST"])
def updateW():
    global W
    W = float(request.form["Wnew"])
    return ""

# ===== PID SLIDERS =====
@app.route("/updatePID", methods=["POST"])
def updatePID():
    global P, I, D, pid

    P = float(request.form["P"])
    I = float(request.form["I"])
    D = float(request.form["D"])

    with pid_lock:
        pid.tunings = (P, I, D)
        pid.reset()   # 🔥 essentieel bij live tuning

    return ""

@app.route("/pidvalues")
def pidvalues():
    return {
        "P": P,
        "I": I,
        "D": D
    }

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
