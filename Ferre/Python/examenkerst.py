from gpiozero import Button, AngularServo, RGBLED, Motor
from time import sleep
import os
import sys
import threading

# Apparaten instellen
rgb_led = RGBLED(red=19, green=13, blue=11)
button1 = Button(6, pull_up=False, bounce_time=0.05)  
button2 = Button(5, pull_up=False, bounce_time=0.05)  
motor = Motor(forward=23, backward=24)
servo = AngularServo(17, initial_angle=0, min_angle=0, max_angle=180, min_pulse_width=7/10000, max_pulse_width=27/10000)
hoek=0
hoek_array1 = [0,15,30,45]
hoek_array2=[45,60,75,90]
hoek_array3=[90,105,120,135]
hoek_array4=[135,150,165,180]
Duty=0
def LEDverander():
        rgb_led.red=1
        sleep(2)
        print("rood")
        os.system('clear')
        rgb_led.green=1
        print("groen")
        sleep(2)
        os.system('clear')
        rgb_led.color = (0, 0, 1)  # Blauw
        print("blauw")
        sleep(2)
        os.system('clear')
        rgb_led.color=(1,1,1)
        print("wit")
        sleep(2)
        os.system('clear')
        rgb_led.color = (0, 0, 0) 
        print("uit")
        sleep(2)
        os.system('clear')
def LEDRED():
    rgb_led.red=1
def LEDGREEN():
    rgb_led.green=1
def LEDBLUE():
     rgb_led.blue=1
def kleurvasthouden():
    if rgb_led.red==1:
        LEDRED()
    elif rgb_led.green==1:
         LEDGREEN
    elif rgb_led.blue==1:
         LEDBLUE()
def helderheid():
    for n in range(100):
        rgb_led.blue = (n/100)		#stuur een getal tussen 0 en 1 naar blue om de helderheid te bepalen
        sleep(0.1)

def servoaansturing():
        RGBLED=threading.Thread(target=LEDverander)
        RGBLED.daemon=True
        RGBLED.start()
        if rgb_led.red==True:
            for hoek in hoek_array1:
                servo.angle = hoek
                pulse_width = servo.pulse_width
                print(f"Servo-hoek: {hoek} graden, Pulsbreedte: {pulse_width * 1000:.2f} ms")
                sleep(0.66)

        elif rgb_led.green==True:
            for hoek in hoek_array2:
                servo.angle = hoek
                pulse_width = servo.pulse_width
                print(f"Servo-hoek: {hoek} graden, Pulsbreedte: {pulse_width * 1000:.2f} ms")
                sleep(0.66)
        elif rgb_led.blue==True:
            for hoek in hoek_array3:
                servo.angle = hoek
                pulse_width = servo.pulse_width
                print(f"Servo-hoek: {hoek} graden, Pulsbreedte: {pulse_width * 1000:.2f} ms")                
                sleep(0.66)
        elif rgb_led.color==(1,1,1):
            for hoek in hoek_array4:
                servo.angle = hoek
                pulse_width = servo.pulse_width
                print(f"Servo-hoek: {hoek} graden, Pulsbreedte: {pulse_width * 1000:.2f} ms")                
                sleep(0.66)
     
try:
    button1.when_pressed = kleurvasthouden 
    button2.when_pressed = helderheid  
    while True:
         servoaansturing()
         sleep(1)

except KeyboardInterrupt:
    motor.off()
    rgb_led.off()
    sys.exit()
