from gpiozero import Button
from time import sleep
from adafruit_servokit import ServoKit
import random
import threading
import pygame
import os
import board
import neopixel

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

# Onthoudt welke posities al juist zijn
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
    'B': 40,
    'C': 80,
    'D': 20
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
    print("Ledstrip gestart.")
except Exception as e:
    pixels = None
    ledstrip_werkt = False
    print(f"Ledstrip werkt niet, spel gaat verder zonder ledstrip: {e}")

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
        print(f"Fout: geluid niet gevonden op {GELUID_PAD}")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(GELUID_PAD)

        print("Code gekraakt! Geluid wordt afgespeeld...")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            sleep(0.1)

    except Exception as e:
        print(f"Er ging iets mis bij het afspelen: {e}")

    finally:
        pygame.mixer.quit()

# =========================
# SPELFUNCTIES
# =========================

def maak_code():
    code = ['A', 'B', 'C', 'D']
    random.shuffle(code)
    return code

def toon_code(code):
    print("\n==================")
    print("NIEUWE CODE:")
    print(" ".join(code))
    print("==================\n")

def servo_omhoog(letter):
    kanaal = servo_map[letter]

    try:
        print(f"Servo {letter} op kanaal {kanaal} omhoog")
        kit.servo[kanaal].angle = servo_omhoog_hoek[letter]
    except Exception as e:
        print(f"FOUT bij servo omhoog {letter}: {e}")

def servo_omlaag(letter):
    kanaal = servo_map[letter]

    try:
        print(f"Servo {letter} op kanaal {kanaal} omlaag")
        kit.servo[kanaal].angle = servo_omlaag_hoek[letter]
    except Exception as e:
        print(f"FOUT bij servo omlaag {letter}: {e}")

def alle_servos_omlaag():
    print("Alle servo's gaan naar beneden...")

    for letter in switches:
        servo_omlaag(letter)

    sleep(1)

def start_standen_opslaan():
    for letter, btn in switches.items():
        vorige_stand[letter] = btn.is_pressed

def wacht_op_omzetting():
    while True:
        for letter, btn in switches.items():
            huidige_stand = btn.is_pressed

            if huidige_stand != vorige_stand[letter]:
                vorige_stand[letter] = huidige_stand

                if huidige_stand:
                    print(f"Schakelaar {letter} is omgezet naar AAN")
                else:
                    print(f"Schakelaar {letter} is omgezet naar UIT")

                servo_omhoog(letter)
                sleep(0.2)
                return letter

        sleep(0.05)

def lees_poging():
    indrukken = vaste_posities.copy()

    print("Zet alleen de foute schakelaars opnieuw om...")

    for i in range(4):
        if indrukken[i] is not None:
            print(f"Positie {i + 1} staat al juist: {indrukken[i]}")
        else:
            print(f"Geef positie {i + 1} in:")
            letter = wacht_op_omzetting()
            indrukken[i] = letter

    return indrukken

# =========================
# HOOFDSPEL
# =========================

try:
    led_thread = threading.Thread(target=led_chaos)
    led_thread.daemon = True
    led_thread.start()

    alle_servos_omlaag()
    start_standen_opslaan()

    code = maak_code()
    toon_code(code)
    poging = 0

    while True:
        indruk = lees_poging()

        poging += 1
        print(f"\nPoging {poging}:")
        print(f"Code is: {' '.join(code)}")
        print(f"Jij bent: {' '.join(indruk)}\n")

        correct = 0

        for i in range(4):
            juiste = code[i]
            gekozen = indruk[i]

            if gekozen == juiste:
                print(f"Positie {i + 1}: {juiste} - GOED!")
                vaste_posities[i] = juiste
                correct += 1
            else:
                print(f"Positie {i + 1}: fout! (jij deed {gekozen}, moet {juiste} zijn)")
                vaste_posities[i] = None
                servo_omlaag(gekozen)

        print(f"\n==> {correct}/4 correct!\n")

        if correct == 4:
            print("YEEEEES! JE HEBT GEWONNEN!!!\n")

            speel_succes_geluid()

            alle_servos_omlaag()
            code = maak_code()
            toon_code(code)
            poging = 0
            vaste_posities = [None, None, None, None]

        sleep(0.5)

except KeyboardInterrupt:
    print("\nSpel gestopt!")

finally:
    leds_actief = False
    sleep(0.5)

    if ledstrip_werkt and pixels is not None:
        pixels.fill((0, 0, 0))
        pixels.show()

    alle_servos_omlaag()
    print("Alles netjes afgesloten.")