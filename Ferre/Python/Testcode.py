from time import sleep, gmtime, strftime
import pymysql
from gpiozero import MCP3008, AngularServo
import busio, board
from flask import Flask, render_template, request
import threading
import os




# -------------------------
# Potmeter & Servo
# -------------------------
pot = MCP3008(channel=0)
servo = AngularServo(17, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
app = Flask(
    __name__,
    static_folder='www',
    static_url_path='/www',
    template_folder='www'
)

maxservo=90
@app.route("/")
def index():
    # Laadt index.html vanuit template_folder
    return render_template("index.html")

@app.route("/max", methods=["POST", "GET"])
def gewenste():
    global maxservo
    getal = request.values.get("getal")

    if getal == "+":
        maxservo += 10
        if maxservo>90:
            maxservo=90
    elif getal == "-":
        maxservo -= 10
        if maxservo<0:
            maxservo=0
    else:
        maxservo=maxservo

    return str(maxservo)

@app.route("/tijd")
def tijd():
    return (
        f" adc value(0-1):{pot.value:.2f}")
        

@app.route("/kalibratie", methods=["POST", "GET"])
def kalibratie():
    global pot_value,kalpot
    kal = request.values.get("kal")
    if kal=="k":
        pot_value=0
    else:
        print("iets")

    return(pot_value)
        



if __name__ == "__main__":

    flask_thread = threading.Thread(
            target=lambda: app.run(
                host="0.0.0.0",
                port=5050,
                debug=True,
                threaded=True,
                use_reloader=False
            ),
            daemon=True
        )

    flask_thread.start()

try:
    while True:
        os.system('clear')
        # --- Sensor uitlezen ---
        pot_value = int(pot.value * 100)

        # --- Servo hoek berekenen ---
        if pot_value>=90:
            pot_value=90
        if pot_value>=maxservo:
            pot_value=maxservo
        servo.angle=pot_value




        # --- Timestamp genereren ---
        print(f"Potmeter: {pot_value:3d}% |  Servo: {servo.angle:6.1f}°")
        print(pot.value)

        sleep(0.5)

except KeyboardInterrupt:
    print("\nStoppen door gebruiker...")

finally:
    servo.value = None

