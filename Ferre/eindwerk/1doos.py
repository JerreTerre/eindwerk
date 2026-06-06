from gpiozero import Button, OutputDevice
from time import sleep
from adafruit_servokit import ServoKit

# --- Modus schakelaar ---
MODUS_NORMAAL_PIN = 27
MODUS_PLAAG_PIN = 22

modus_normaal = Button(MODUS_NORMAAL_PIN, pull_up=False)
modus_plaag = Button(MODUS_PLAAG_PIN, pull_up=False)

# --- Doos componenten ---
SCHAKELAAR_PIN = 6
SENSOR_PIN = 17
SOLENOID_PIN = 25

schakelaar = Button(SCHAKELAAR_PIN, pull_up=False)
sensor = Button(SENSOR_PIN, pull_up=False)

solenoid = OutputDevice(SOLENOID_PIN, active_high=False, initial_value=False)

# --- Servo's ---
kit = ServoKit(channels=16)

SERVO_NORMAAL_CHANNEL = 4
SERVO_PLAAG_CHANNEL = 5

# Nieuwe hoeken configuratie
SERVO_NORMAAL_START = 0
SERVO_NORMAAL_MAX = 75

SERVO_PLAAG_START = 110
SERVO_PLAAG_ACTIE = 0

# Zet servo's direct in hun juiste beginpositie bij het opstarten
kit.servo[SERVO_NORMAAL_CHANNEL].angle = SERVO_NORMAAL_START
kit.servo[SERVO_PLAAG_CHANNEL].angle = SERVO_PLAAG_START

# --- Status variabelen ---
vorige_schakelaar = False
vorige_sensor = False
vorige_modus = None

def lees_modus():
    if modus_normaal.is_pressed:
        return "normaal"
    if modus_plaag.is_pressed:
        return "plaag"
    return "pauze"

try:
    print("Doos gestart. Druk op Ctrl+C om te stoppen.")

    while True:
        modus = lees_modus()

        if modus != vorige_modus:
            print(f"\nHuidige modus: {modus}")
            vorige_modus = modus

        # --- 1. Sensor en Solenoid (Alleen in plaagmodus) ---
        if modus == "plaag":
            if sensor.is_pressed:
                if not vorige_sensor:
                    print("Sensor detecteert iets -> Solenoid AAN")
                    solenoid.on()
                    vorige_sensor = True
            else:
                if vorige_sensor:
                    print("Sensor detecteert niets meer -> Solenoid UIT")
                    solenoid.off()
                    vorige_sensor = False
        else:
            if vorige_sensor:
                solenoid.off()
                vorige_sensor = False

        # --- 2. Schakelaar en Servo's ---
        if schakelaar.is_pressed:
            if not vorige_schakelaar:
                vorige_schakelaar = True
                print("Schakelaar is AANGEZET")
                
                if modus == "normaal":
                    print("-> Actie: Servo 4 naar 75 graden")
                    kit.servo[SERVO_NORMAAL_CHANNEL].angle = SERVO_NORMAAL_MAX
                elif modus == "plaag":
                    print("-> Actie: Servo 5 naar 0 graden")
                    kit.servo[SERVO_PLAAG_CHANNEL].angle = SERVO_PLAAG_ACTIE
        else:
            if vorige_schakelaar:
                vorige_schakelaar = False
                print("Schakelaar is UITGEZET -> Alle servo's naar hun startpositie")
                # Servo 4 gaat terug naar 0, Servo 5 gaat terug naar 110
                kit.servo[SERVO_NORMAAL_CHANNEL].angle = SERVO_NORMAAL_START
                kit.servo[SERVO_PLAAG_CHANNEL].angle = SERVO_PLAAG_START

        sleep(0.1)

except KeyboardInterrupt:
    print("\nProgramma gestopt.")
    solenoid.off()
    kit.servo[SERVO_NORMAAL_CHANNEL].angle = SERVO_NORMAAL_START
    kit.servo[SERVO_PLAAG_CHANNEL].angle = SERVO_PLAAG_START