from gpiozero import OutputDevice, Button
from time import sleep
import board
import neopixel
from adafruit_servokit import ServoKit

# --- Configuratie pinnen ---
DRUKKNOP_PINNEN = [12, 6, 13, 26]
SENSOR_PINNEN = [14, 15, 17, 23]
SOLENOID_PINNEN = [4, 25, 24, 18]

# --- 3-way switch ---
SWITCH_NORMAAL_PIN = 22
SWITCH_STOORZENDER_PIN = 27

switch_normaal = Button(SWITCH_NORMAAL_PIN, pull_up=False)
switch_stoorzender = Button(SWITCH_STOORZENDER_PIN, pull_up=False)

# --- Servo kanalen per doosje ---
SERVO_CHANNELS = [
    [0, 1],
    [5, 6],
    [8, 9],
    [12, 13],
]

SERVO_DICHT = 0
SERVO_OPEN = 90

kit = ServoKit(channels=16)

for servo_paar in SERVO_CHANNELS:
    for channel in servo_paar:
        kit.servo[channel].angle = SERVO_DICHT

# --- Initialiseer drukknoppen, sensoren en solenoids ---
drukknoppen = [Button(pin, pull_up=False) for pin in DRUKKNOP_PINNEN]
sensoren = [Button(pin, pull_up=False) for pin in SENSOR_PINNEN]

solenoids = [
    OutputDevice(pin, active_high=False, initial_value=False)
    for pin in SOLENOID_PINNEN
]

# --- Configuratie LED Strip ---
LED_PIN = board.MOSI         # GPIO 10
NUM_LEDS = 60
BRIGHTNESS = 0.2

pixels = neopixel.NeoPixel(
    LED_PIN,
    NUM_LEDS,
    brightness=BRIGHTNESS,
    auto_write=False
)

# --- Kleuren ---
KLEUR_ACHTERGROND = (0, 0, 0)

KLEUREN = [
    (255, 0, 0),      # Rood
    (0, 255, 0),      # Groen
    (0, 0, 255),      # Blauw
    (255, 255, 0),    # Geel
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyaan
]

previous_sensor_states = [None, None, None, None]
previous_button_states = [None, None, None, None]

led_count = 0
vorige_modus = None

# Juiste volgorde van de doosjes in normale spelmodus
JUISTE_VOLGORDE = [0, 1, 2, 3]
huidige_stap = 0


def alle_solenoids_uit():
    for solenoid in solenoids:
        solenoid.off()


def alle_servos_dicht():
    for servo_paar in SERVO_CHANNELS:
        for channel in servo_paar:
            kit.servo[channel].angle = SERVO_DICHT


def leds_uit():
    pixels.fill((0, 0, 0))
    pixels.show()


def voeg_leds_toe(aantal=10):
    global led_count

    kleur_index = (led_count // 10) % len(KLEUREN)
    kleur = KLEUREN[kleur_index]

    for i in range(aantal):
        if led_count < NUM_LEDS:
            pixels[led_count] = kleur
            led_count += 1

    pixels.show()


def lees_modus():
    if switch_normaal.is_pressed:
        return "normaal"

    if switch_stoorzender.is_pressed:
        return "stoorzender"

    return "pauze"


try:
    print(f"LED-strip gestart voor {NUM_LEDS} leds op GPIO 10...")
    print("3-way switch:")
    print("GPIO 22 = normale spelmodus")
    print("Middenstand = pauze")
    print("GPIO 27 = stoorzender-modus")
    print("Druk op Ctrl+C om te stoppen.")

    leds_uit()

    while True:
        modus = lees_modus()

        if modus != vorige_modus:
            print(f"Modus veranderd naar: {modus}")
            vorige_modus = modus

            alle_solenoids_uit()
            alle_servos_dicht()

        # --- Middenstand: alles uit ---
        if modus == "pauze":
            alle_solenoids_uit()
            alle_servos_dicht()
            sleep(0.1)
            continue

        # --- Normale spelmodus ---
        if modus == "normaal":
            for index in range(4):
                sensor = sensoren[index]
                drukknop = drukknoppen[index]
                solenoid = solenoids[index]
                servo_paar = SERVO_CHANNELS[index]

                # Sensor bestuurt solenoid en LED-strip
                if sensor.is_pressed:
                    if previous_sensor_states[index] != True:
                        print(f"Sensor {index + 1} detecteert - Solenoid {index + 1} AAN")
                        previous_sensor_states[index] = True
                        voeg_leds_toe(10)

                    solenoid.on()

                else:
                    if previous_sensor_states[index] != False:
                        print(f"Sensor {index + 1} detecteert niets - Solenoid {index + 1} UIT")
                        previous_sensor_states[index] = False

                    solenoid.off()

                # Drukknoppen moeten in juiste volgorde worden ingedrukt
                if drukknop.is_pressed:
                    if previous_button_states[index] != True:
                        previous_button_states[index] = True

                        if index == JUISTE_VOLGORDE[huidige_stap]:
                            print(f"Correct: doosje {index + 1}")

                            for channel in servo_paar:
                                kit.servo[channel].angle = SERVO_OPEN

                            huidige_stap += 1

                            if huidige_stap >= len(JUISTE_VOLGORDE):
                                print("Volledige juiste volgorde voltooid!")
                                huidige_stap = 0

                        else:
                            print(f"Fout: doosje {index + 1}, volgorde opnieuw starten")
                            huidige_stap = 0
                            alle_servos_dicht()

                else:
                    if previous_button_states[index] != False:
                        previous_button_states[index] = False

        # --- Stoorzender-modus ---
        if modus == "stoorzender":
            for index in range(4):
                drukknop = drukknoppen[index]
                servo_paar = SERVO_CHANNELS[index]

                if drukknop.is_pressed:
                    if previous_button_states[index] != True:
                        print(f"Stoorzender: drukknop {index + 1} ingedrukt")
                        previous_button_states[index] = True

                    # In stoorzender-modus reageren de servo's direct
                    for channel in servo_paar:
                        kit.servo[channel].angle = SERVO_OPEN

                    # Solenoid kort aan als storend effect
                    solenoids[index].on()

                else:
                    if previous_button_states[index] != False:
                        previous_button_states[index] = False

                    for channel in servo_paar:
                        kit.servo[channel].angle = SERVO_DICHT

                    solenoids[index].off()

        sleep(0.1)

except KeyboardInterrupt:
    print("Gestopt")

    alle_solenoids_uit()
    alle_servos_dicht()
    leds_uit()