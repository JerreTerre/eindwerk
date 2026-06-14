from flask import Flask, jsonify, render_template
from gpiozero import Button
from time import sleep
from adafruit_servokit import ServoKit
import random
import threading
import pygame
import os
import subprocess
import board
import neopixel

# =========================
# FLASK
# =========================

app = Flask(__name__, static_url_path="", static_folder="www", template_folder="www")

data_lock = threading.Lock()

laatste_poging = ["-", "-", "-", "-"]
pogingen_teller = 0
gegokte_codes = []
laatste_bericht = "Spel wordt gestart..."
laatste_score = 0

# =========================
# INSTELLINGEN
# =========================

PULL_UP = False

GELUID_PAD = "/home/pi/Ferre/eindwerk/geluid/insomnia.mp3"

LED_PIN = board.MOSI
NUM_LEDS = 60
BRIGHTNESS = 0.2

leds_actief = True
ledstrip_werkt = False
spel_actief = True

vaste_posities = [None, None, None, None]

# =========================
# SCHAKELAARS
# =========================

schakelaarA = Button(12, pull_up=PULL_UP, bounce_time=0.05)
schakelaarB = Button(6, pull_up=PULL_UP, bounce_time=0.05)
schakelaarC = Button(13, pull_up=PULL_UP, bounce_time=0.05)
schakelaarD = Button(26, pull_up=PULL_UP, bounce_time=0.05)

switches = {
    'A': schakelaarA,
    'B': schakelaarB,
    'C': schakelaarC,
    'D': schakelaarD
}

vorige_stand = {}

# =========================
# SERVO'S
# =========================

servo_map = {
    'A': 0,
    'B': 4,
    'C': 8,
    'D': 12
}

servo_omhoog_hoek = {
    'A': 90,
    'B': 20,
    'C': 100,
    'D': 30
}

servo_omlaag_hoek = {
    'A': 20,
    'B': 90,
    'C': 20,
    'D': 90
}

kit = ServoKit(channels=16)

# =========================
# LEDSTRIP
# =========================

try:
    pixels = neopixel.NeoPixel(
        LED_PIN,
        NUM_LEDS,
        brightness=BRIGHTNESS,
        auto_write=False
    )
    ledstrip_werkt = True
except Exception:
    pixels = None
    ledstrip_werkt = False


def zet_bericht(tekst):
    global laatste_bericht
    with data_lock:
        laatste_bericht = tekst


def wheel(pos):
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)


def led_chaos():
    global leds_actief

    if not ledstrip_werkt or pixels is None:
        return

    while leds_actief:
        effect = random.randint(1, 3)

        if effect == 1:
            for stap in range(256):
                if not leds_actief:
                    break
                for i in range(NUM_LEDS):
                    kleur = wheel((i * 256 // NUM_LEDS + stap) & 255)
                    pixels[i] = kleur
                pixels.show()
                sleep(0.02)

        elif effect == 2:
            for _ in range(80):
                if not leds_actief:
                    break
                for i in range(NUM_LEDS):
                    pixels[i] = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)
                    )
                pixels.show()
                sleep(0.05)

        elif effect == 3:
            pixels.fill((0, 0, 0))
            pixels.show()

            for i in range(NUM_LEDS):
                if not leds_actief:
                    break

                eindpunt = NUM_LEDS - i

                for j in range(eindpunt):
                    if not leds_actief:
                        break

                    pixels[j] = (0, 0, 255)

                    if j > 0:
                        pixels[j - 1] = (0, 0, 0)

                    pixels.show()
                    sleep(0.005)

                pixels[eindpunt - 1] = (255, 255, 255)
                pixels.show()

    pixels.fill((0, 0, 0))
    pixels.show()

# =========================
# GELUID
# =========================


def speel_succes_geluid():
    if not os.path.exists(GELUID_PAD):
        zet_bericht(f"Fout: geluid niet gevonden op {GELUID_PAD}")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(GELUID_PAD)
        zet_bericht("Code gekraakt! Geluid wordt afgespeeld...")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            sleep(0.1)

    except Exception as e:
        zet_bericht(f"Er ging iets mis bij het afspelen: {e}")

    finally:
        pygame.mixer.quit()

# =========================
# SPELFUNCTIES
# =========================


def maak_code():
    code = ['A', 'B', 'C', 'D']
    random.shuffle(code)
    return code


def servo_omhoog(letter):
    kanaal = servo_map[letter]
    try:
        kit.servo[kanaal].angle = servo_omhoog_hoek[letter]
    except Exception as e:
        zet_bericht(f"FOUT bij servo omhoog {letter}: {e}")


def servo_omlaag(letter):
    kanaal = servo_map[letter]
    try:
        kit.servo[kanaal].angle = servo_omlaag_hoek[letter]
    except Exception as e:
        zet_bericht(f"FOUT bij servo omlaag {letter}: {e}")


def alle_servos_omlaag():
    zet_bericht("Alle servo's gaan naar beneden...")
    for letter in switches:
        servo_omlaag(letter)
    sleep(1)


def start_standen_opslaan():
    for letter, btn in switches.items():
        vorige_stand[letter] = btn.is_pressed


def wacht_op_omzetting():
    while spel_actief:
        for letter, btn in switches.items():
            huidige_stand = btn.is_pressed

            if huidige_stand != vorige_stand[letter]:
                vorige_stand[letter] = huidige_stand
                servo_omhoog(letter)
                sleep(0.2)
                return letter

        sleep(0.05)

    return None


def lees_poging():
    global laatste_poging

    indrukken = vaste_posities.copy()

    with data_lock:
        laatste_poging = ["-", "-", "-", "-"]

    zet_bericht("Zet alleen de foute schakelaars opnieuw om...")

    for i in range(4):
        if indrukken[i] is not None:
            with data_lock:
                laatste_poging[i] = indrukken[i]
        else:
            zet_bericht(f"Geef positie {i + 1} in:")
            letter = wacht_op_omzetting()

            if letter is None:
                return None

            indrukken[i] = letter

            with data_lock:
                laatste_poging[i] = letter

    return indrukken


def reset_webdata():
    global laatste_poging, pogingen_teller, gegokte_codes, laatste_score

    with data_lock:
        laatste_poging = ["-", "-", "-", "-"]
        pogingen_teller = 0
        gegokte_codes = []
        laatste_score = 0

# =========================
# FLASK ROUTES
# =========================


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/values")
def values():
    with data_lock:
        return jsonify(
            dozen=["A", "B", "C", "D"],
            laatste_poging=laatste_poging.copy(),
            pogingen=pogingen_teller,
            gegokte_codes=gegokte_codes.copy(),
            bericht=laatste_bericht,
            score=laatste_score
        )


@app.route("/rebootPi", methods=["POST"])
def reboot_pi():
    subprocess.Popen(["sudo", "reboot"])
    return "ok"


@app.route("/shutdownPi", methods=["POST"])
def shutdown_pi():
    subprocess.Popen(["sudo", "shutdown", "-h", "now"])
    return "ok"

# =========================
# HOOFDSPEL
# =========================


def start_spel():
    global poging, vaste_posities, pogingen_teller, gegokte_codes, laatste_score

    try:
        alle_servos_omlaag()
        start_standen_opslaan()

        code = maak_code()
        poging = 0

        while spel_actief:
            indruk = lees_poging()

            if indruk is None:
                break

            poging += 1

            correct = 0

            for i in range(4):
                juiste = code[i]
                gekozen = indruk[i]

                if gekozen == juiste:
                    vaste_posities[i] = juiste
                    correct += 1
                else:
                    vaste_posities[i] = None
                    servo_omlaag(gekozen)

            with data_lock:
                pogingen_teller = poging
                laatste_score = correct
                gegokte_codes.insert(0, {
                    "poging": poging,
                    "code": " ".join(indruk),
                    "score": f"{correct}/4"
                })

            zet_bericht(f"{correct}/4 correct")

            if correct == 4:
                zet_bericht("YEEEEES! JE HEBT GEWONNEN!!!")

                speel_succes_geluid()

                alle_servos_omlaag()
                code = maak_code()
                poging = 0
                vaste_posities = [None, None, None, None]
                reset_webdata()

            sleep(0.5)

    except KeyboardInterrupt:
        zet_bericht("Spel gestopt!")


if __name__ == "__main__":
    try:
        led_thread = threading.Thread(target=led_chaos)
        led_thread.daemon = True
        led_thread.start()

        spel_thread = threading.Thread(target=start_spel)
        spel_thread.daemon = True
        spel_thread.start()

        app.run(host="0.0.0.0", port=5050, debug=False, use_reloader=False)

    finally:
        spel_actief = False
        leds_actief = False
        sleep(0.5)

        if ledstrip_werkt and pixels is not None:
            pixels.fill((0, 0, 0))
            pixels.show()

        alle_servos_omlaag()
