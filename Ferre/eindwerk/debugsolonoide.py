from gpiozero import OutputDevice
from time import sleep

# De solenoid is aangesloten op pin 25
SOLENOID_PIN = 16

solenoid = OutputDevice(SOLENOID_PIN, active_high=False, initial_value=False)
try:
    while True:
        print("Solenoid gaat AAN")
        solenoid.on()

        sleep(2)

        print("Solenoid gaat UIT")
        solenoid.off()
        sleep(2)
except KeyboardInterrupt:
    print("Gestopt")
    solenoid.off()