from gpiozero import Button, AngularServo, RGBLED, Servo
from time import sleep
import os
import sys
import threading

# RGB LED configuratie
rgb_led = RGBLED(red=10, green=13, blue=19)

# Knoppen configureren
button1 = Button(6, pull_up=False, bounce_time=0.05)
button2 = Button(5, pull_up=False, bounce_time=0.05)

# Servo configureren
servo = AngularServo(17, initial_angle=0, min_angle=0, max_angle=180, min_pulse_width=7/10000, max_pulse_width=27/10000)

# Globale variabelen
Duty_cycle = 0
hoek=0
hoeken = [0,18,36,54,72,90,108,126,144,162,180]
tijdaan=0.5
frequentie=0.5
Duty_cycle=0.5
def LEDRED():
    aan=(1/frequentie)/Duty_cycle
    uit=(1/frequentie)/(1-Duty_cycle)
    rgb_led.red = 1  # Zet de rode kleur aan
    sleep(aan)  # Wacht tijdens de aan-tijd
    rgb_led.red = 0  # Zet de rode kleur uit
    

def dalenslagboom():
    rgb_led.green=1
    sleep(7)
    print("Rij door") 
    rgb_led.green=0 
    rgb_led.blue=1 
    sleep(3)
    
    rgb_led.blue=0
    print("slagboom komt naar beneden")
    for hoek in reversed(hoeken):
        servo.angle=hoek
        sleep(0.2)

        
def openslagboom():
    global hoeken
    global hoek
    sleep(2)
    for hoek in hoeken:
        servo.angle=hoek
        sleep(0.2)
    


def drukknop1():
    openslagboom()
    dalenslagboom()

try:
    LED_thread = threading.Thread(target=LEDRED)
    LED_thread.daemon = True
    button1.when_pressed = drukknop1

    
    while True:
        if hoek==0:
            LEDRED()
        os.system('clear')
        print("Servo Angle =", hoek, "°")
        sleep(5)
        

except KeyboardInterrupt:
    rgb_led.off()  
    sys.exit()
