from gpiozero import Button, OutputDevice
from time import sleep
from adafruit_servokit import ServoKit

# Modus knoppen
modus_normaal = Button(27, pull_up=False)
modus_plaag = Button(22, pull_up=False)

# Bestaande sets
schakelaar3 = Button(13, pull_up=False)
schakelaar4 = Button(26, pull_up=False)
sensor4 = Button(14, pull_up=False)
sensor3 = Button(15, pull_up=False)
solenoid4 = OutputDevice(25, active_high=False, initial_value=False)
solenoid3 = OutputDevice(16, active_high=False, initial_value=False)

# Eerste extra set (pin 6, 23, 24) — eerder toegevoegd
schakelaar5 = Button(6, pull_up=False)
sensor5 = Button(23, pull_up=False)
solenoid5 = OutputDevice(24, active_high=False, initial_value=False)

# Nieuwe set zoals gevraagd (pin 12, 17, 4)
schakelaar6 = Button(12, pull_up=False)     # schakelaar op pin 12
sensor6 = Button(17, pull_up=False)         # sensor op pin 17
solenoid6 = OutputDevice(4, active_high=False, initial_value=False)   # solenoid op pin 4

# Servokit (16 kanalen)
kit = ServoKit(channels=16)

try:
    while True:
        if modus_plaag.is_pressed:

            # --- Set 3 (Plaagmodus) ---
            if sensor3.is_pressed:
                solenoid3.on()
            else:
                solenoid3.off()

            try:
                if schakelaar3.is_pressed:
                    kit.servo[9].angle = 0
                else:
                    kit.servo[9].angle = 160
            except OSError:
                print("I2C storing opgevangen bij servo 9 (plaagmodus)")

            # --- Set 4 (Plaagmodus) ---
            if sensor4.is_pressed:
                solenoid4.on()
            else:
                solenoid4.off()

            try:
                if schakelaar4.is_pressed:
                    kit.servo[13].angle = 0
                else:
                    kit.servo[13].angle = 160
            except OSError:
                print("I2C storing opgevangen bij servo 13 (plaagmodus)")

            # --- Set 5 (Plaagmodus) ---
            if sensor5.is_pressed:
                solenoid5.on()
            else:
                solenoid5.off()

            try:
                if schakelaar5.is_pressed:
                    kit.servo[5].angle = 175
                else:
                    kit.servo[5].angle = 0
            except OSError:
                print("I2C storing opgevangen bij servo 5 (plaagmodus)")

            # --- Nieuwe Set 6 (Plaagmodus) ---
            if sensor6.is_pressed:
                solenoid6.on()
            else:
                solenoid6.off()

            try:
                # servo plaag op channel 1
                if schakelaar6.is_pressed:
                    kit.servo[1].angle = 160
                else:
                    kit.servo[1].angle = 0
            except OSError:
                print("I2C storing opgevangen bij servo 1 (plaagmodus)")

        elif modus_normaal.is_pressed:

            # --- Set 3 (Normale modus) ---
            try:
                if schakelaar3.is_pressed:
                    kit.servo[8].angle = 80
                else:
                    kit.servo[8].angle = 20
            except OSError:
                print("I2C storing opgevangen bij servo 8 (normale modus)")

            # --- Set 4 (Normale modus) ---
            try:
                if schakelaar4.is_pressed:
                    kit.servo[12].angle = 20
                else:
                    kit.servo[12].angle = 75
            except OSError:
                print("I2C storing opgevangen bij servo 12 (normale modus)")

            # --- Set 5 (Normale modus) ---
            try:
                if schakelaar5.is_pressed:
                    kit.servo[4].angle = 90
                else:
                    kit.servo[4].angle = 20
            except OSError:
                print("I2C storing opgevangen bij servo 4 (normale modus)")

            # --- Nieuwe Set 6 (Normale modus) ---
            try:
                # servo normaal op channel 0
                if schakelaar6.is_pressed:
                    kit.servo[0].angle = 20
                else:
                    kit.servo[0].angle = 90
            except OSError:
                print("I2C storing opgevangen bij servo 0 (normale modus)")

        # Korte rustpauze voor de processor
        sleep(0.05)

except KeyboardInterrupt:
    print("Gestopt")
    # Zet solenoids veilig uit
    solenoid4.off()
    solenoid3.off()
    solenoid5.off()
    solenoid6.off()

    # Veilig afsluiten van de servo's proberen we ook binnen een try-except
    try:
        kit.servo[13].angle = 160
        kit.servo[12].angle = 90
        kit.servo[9].angle = 160
        kit.servo[8].angle = 20
        kit.servo[5].angle = 160
        kit.servo[4].angle = 90
        kit.servo[1].angle = 160  # eindpositie voor plaag-servo van set 6
        kit.servo[0].angle = 90   # eindpositie voor normaal-servo van set 6
    except OSError:
        print("Kon eindposities servo's niet instellen bij afsluiten door I2C storing.")
