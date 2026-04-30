from gpiozero import PWMLED
from time import sleep
from simple_pid import PID
from threading import Lock
import _thread
from flask import Flask, request, render_template, jsonify
import busio
import board
import adafruit_bmp280
import pymysql
import sys
import spidev

# --- I2C en BMP280 configuratie ---
# Initialiseer de I2C bus (SCL op pin 3, SDA op pin 5)
i2c = busio.I2C(board.SCL, board.SDA)
# Maak verbinding met de BMP280 sensor via het standaard I2C adres 0x76
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

# --- PWM LED Configuratie ---
# Initialiseer een PWM-gestuurde LED op GPIO pin 27
pwm_device = PWMLED(27)
pwm_device.value = 0  # Start de LED in uitgeschakelde toestand (0%)

# ============================================================
# VARIABELEN & PID-INSTELLINGEN
# ============================================================
tempX = 0.0             # Werkelijke waarde (X): Gemeten door de BMP280
W = 20.0                # Gewenste waarde (W): Setpoint ingesteld via Pot of Slider
y = 0.0                 # Stuurwaarde (Y): De berekende PWM-output in % (0-100)
P = 1.5                 # Proportionele actie: De versterkingsfactor van de regelaar
use_potentiometer = True # Boolean om te schakelen tussen Hardware (Pot) en Software (Slider)

# Initialiseer de PID bibliotheek als een P-regelaar (I en D staan op 0)
# setpoint: de waarde die we willen bereiken (W)
pid = PID(P, 0, 0, setpoint=W)
pid.sample_time = 0.1      # Berekening vindt elke 0.1 seconden plaats
pid.output_limits = (0, 100) # De output (Y) wordt begrensd tussen 0% en 100%

# Lock mechanisme om data-conflicten tussen de Regel-thread en de Flask-thread te voorkomen
pid_lock = Lock()

# --- Database connectie instellen ---
conn = pymysql.connect(
    host='127.0.0.1',
    unix_socket='/var/run/mysqld/mysqld.sock', # Verbinding via lokale socket (sneller op Pi)
    user='Smets',
    passwd='Thomas',
    db='VBexaam'
)
cur = conn.cursor()

# --- SPI en MCP3008 (ADC) configuratie ---
spi = spidev.SpiDev()
spi.open(0, 0) # Open SPI bus 0, device (chip select) 0
spi.max_speed_hz = 1350000

def read_mcp3008(channel):
    """Leest de analoge waarde (0-1023) uit van een specifiek kanaal op de MCP3008."""
    if channel < 0 or channel > 7:
        return -1
    # SPI communicatie protocol voor MCP3008: Startbit, Single-ended mode + channel, dummy byte
    adc = spi.xfer2([0x01, 0x80 | (channel << 4), 0x00])
    # Combineer de relevante bits uit de response tot een 10-bit getal
    data = ((adc[1] & 0x03) << 8) | adc[2]
    return data

# ============================================================
# REGELTHREAD (Draait continu op de achtergrond)
# ============================================================
def regel_loop():
    global tempX, y, W, use_potentiometer, P
    try:
        # Maak de tabel leeg bij het opstarten van het script (optioneel voor examen)
        cur.execute("TRUNCATE TABLE waarde")
        conn.commit()

        while True:
            # 1. Meten van de werkelijke waarde (X) via I2C
            tempX = round(bmp280.temperature, 1)

            # 2. Bepalen van de gewenste waarde (W)
            if use_potentiometer:
                # Lees kanaal 0 van de ADC uit
                adc_value = read_mcp3008(0)
                # Schaal de 10-bit waarde (0-1023) naar 0.0 - 1.0 (percentage)
                percentage = (adc_value / 1023.0)
                # Schaal naar temperatuurbereik 0°C tot 50°C (zoals gevraagd in opgave)
                W = round(percentage * 50.0, 1)

            # 3. P-berekening uitvoeren
            with pid_lock:
                pid.setpoint = W          # Update het doel in de PID-regelaar
                pid.tunings = (P, 0, 0)   # Update de P-waarde (mocht deze via Flask gewijzigd zijn)
                y = pid(tempX)            # Bereken de nieuwe output Y op basis van X
            
            # 4. Actuatie: Stuur de LED aan via PWM
            # De LED verwacht een waarde tussen 0.0 en 1.0, dus Y (0-100) delen door 100
            pwm_device.value = y / 100.0

            # 5. Data logging: Sla de waarden op in de MariaDB/MySQL database
            cur.execute("""
                INSERT INTO waarde (time, W, X, Y)
                VALUES (NOW(), %s, %s, %s)
            """, (W, tempX, y))
            conn.commit()

            # Pauzeer de loop voor 200ms om de CPU niet te overbelasten
            sleep(0.2)
    except Exception as e:
        print(f"Error in regel_loop: {e}")
    finally:
        pwm_device.off() # Zet de LED uit als de thread stopt

# Start de bovenstaande functie in een nieuwe achtergrond-thread
_thread.start_new_thread(regel_loop, ())

# ============================================================
# FLASK SERVER (Webinterface)
# ============================================================
app = Flask(__name__, static_url_path="", static_folder="www", template_folder="www")

# Route voor de homepagina
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint om de Setpoint (W) via de slider op de website aan te passen
@app.route("/updateW", methods=["POST"])
def updateW():
    global W, use_potentiometer
    # Pas W alleen aan via de slider als de fysieke potentiometer is uitgeschakeld
    if not use_potentiometer:
        W = float(request.form["Wnew"])
    return ""

# Endpoint om de P-versterkingsfactor aan te passen via de slider
@app.route("/updateP", methods=["POST"])
def updateP():
    global P
    P = float(request.form["P"])
    return ""

# Endpoint om te wisselen tussen de Potentiometer (Hardware) en Slider (Software)
@app.route("/toggleW_source", methods=["POST"])
def toggleW_source():
    global use_potentiometer
    use_potentiometer = not use_potentiometer # Wissel True/False om
    # Stuur de nieuwe status terug naar de browser als JSON
    return jsonify({"use_potentiometer": use_potentiometer})

# Endpoint waar de browser elke 500ms de actuele waarden ophaalt voor de UI
@app.route("/values")
def values():
    return jsonify({
        "X": tempX,
        "W": W,
        "Y": round(y, 1),
        "P": P,
        "use_potentiometer": use_potentiometer
    })

# --- Main Entry Point ---
if __name__ == "__main__":
    app.run(
        debug=True, 
        host="0.0.0.0", # Toegankelijk via het netwerk
        port=5050, 
        use_reloader=False # Belangrijk: voorkomt dat de regel_loop thread twee keer start
    )