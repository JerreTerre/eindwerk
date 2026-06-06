import random
from time import sleep
from adafruit_servokit import ServoKit
from gpiozero import Button, OutputDevice

# ---------------------------
# SETS
# ---------------------------
sets = [
    {
        "naam": "Set 1",
        "schakelaar": Button(12, pull_up=True, bounce_time=0.1),
        "sensor": Button(17, pull_up=True),
        "solenoid": OutputDevice(4, active_high=False, initial_value=False),
        "deur_servo": 0,
        "box_servo": 1,
        "laatste_status": False,
        "gekozen_optie": None,
        "deur_open": False,
    },
    {
        "naam": "Set 2",
        "schakelaar": Button(6, pull_up=True, bounce_time=0.1),
        "sensor": Button(23, pull_up=True),
        "solenoid": OutputDevice(24, active_high=False, initial_value=False),
        "deur_servo": 4,
        "box_servo": 5,
        "laatste_status": False,
        "gekozen_optie": None,
        "deur_open": False,
    },
    {
        "naam": "Set 3",
        "schakelaar": Button(13, pull_up=True, bounce_time=0.1),
        "sensor": Button(15, pull_up=True),
        "solenoid": OutputDevice(16, active_high=False, initial_value=False),
        "deur_servo": 8,
        "box_servo": 9,
        "laatste_status": False,
        "gekozen_optie": None,
        "deur_open": False,
    },
    {
        "naam": "Set 4",
        "schakelaar": Button(26, pull_up=True, bounce_time=0.1),
        "sensor": Button(14, pull_up=True),
        "solenoid": OutputDevice(25, active_high=False, initial_value=False),
        "deur_servo": 12,
        "box_servo": 13,
        "laatste_status": False,
        "gekozen_optie": None,
        "deur_open": False,
    },
]

kit = ServoKit(channels=16)

def stuur_servo(kanaal, hoek):
    try:
        kit.servo[kanaal].angle = hoek
    except Exception as e:
        print(f"Servo fout {kanaal}: {e}")

# ---------------------------
# LOOP
# ---------------------------
try:
    while True:

        # ---------------------------
        # SENSOR → SOLENOID
        # ---------------------------
        for s in sets:
            if not s["sensor"].is_pressed:
                s["solenoid"].on()
            else:
                s["solenoid"].off()

        # ---------------------------
        # SCHAKELAAR LOGICA
        # ---------------------------
        for s in sets:
            actief = not s["schakelaar"].is_pressed  # pull-up

            # FLANK: schakelaar net aangezet
            if actief and not s["laatste_status"]:
                s["gekozen_optie"] = random.choice([1, 2, 3])
                print(f"{s['naam']} → optie {s['gekozen_optie']}")

            # ---------------------------
            # ACTIES
            # ---------------------------
            if actief and s["gekozen_optie"]:

                # OPTIE 1 → schakelaar terug duwen
                if s["gekozen_optie"] == 1:
                    stuur_servo(s["box_servo"], 0)
                    sleep(0.3)
                    stuur_servo(s["box_servo"], 160)
                    s["gekozen_optie"] = None

                # OPTIE 2 → deur open
                elif s["gekozen_optie"] == 2:
                    stuur_servo(s["deur_servo"], 20)
                    s["deur_open"] = True
                    s["gekozen_optie"] = None

                # OPTIE 3 → sluit een open deur ergens
                elif s["gekozen_optie"] == 3:
                    open_deuren = [x for x in sets if x["deur_open"]]

                    if open_deuren:
                        doel = random.choice(open_deuren)
                        stuur_servo(doel["deur_servo"], 90)
                        doel["deur_open"] = False
                        print(f"{doel['naam']} deur gesloten")

                    else:
                        print("Geen open deuren")

                    s["gekozen_optie"] = None

            s["laatste_status"] = actief

        sleep(0.05)

# ---------------------------
# STOP
# ---------------------------
except KeyboardInterrupt:
    print("Stop")

    for s in sets:
        s["solenoid"].off()
        stuur_servo(s["box_servo"], 160)
        stuur_servo(s["deur_servo"], 90)