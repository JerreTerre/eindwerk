from gpiozero import Motor, Button, AngularServo, RGBLED
from time import sleep
import os
import sys
import threading

rgb_led = RGBLED(red=10, green=13, blue=19)
button1 = Button(6, pull_up=False,bounce_time=0.05)
button2 = Button(5, pull_up=False,bounce_time=0.05)
motor = Motor(forward=23, backward=24)
servo = AngularServo(17,initial_angle=0, min_angle=0, max_angle=90, min_pulse_width=7/10000, max_pulse_width=27/10000)

Duty_cycle = 0
angle = 0
frequentie = 1.33

def drukknop1():
    global Duty_cycle, angle
    angle += 18
    Duty_cycle += 10


def indrukkenDruknop1():
    drukknop1

def drukknop2():
    global Duty_cycle, angle
    angle -= 18
    Duty_cycle -= 10

def RGBLED_thread():
    while True:
        rgb_led.color = (1, 0, 0)
        sleep(frequentie)
        rgb_led.color = (0, 1, 0)
        sleep(frequentie)
        rgb_led.color = (0, 0, 1)
        sleep(frequentie)

try:
    LED_thread = threading.Thread(target=RGBLED_thread)
    LED_thread.daemon = True
    LED_thread.start()
    button1.when_pressed = drukknop1
    button2.when_pressed = drukknop2

    while True:
        if angle > 180:
            angle = 180           
        if angle < 0:
            angle = 0 
        servo.angle = angle
        if Duty_cycle > 100:
            Duty_cycle = 100        
        if Duty_cycle < 0:
            Duty_cycle = 0
        motor.forward(Duty_cycle / 100)

        os.system('clear')
        print("Duty Cycle =", Duty_cycle, "%")
        print("Servo Angle =", angle, "°")
        sleep(0.1)
except KeyboardInterrupt:
    motor.off()
    rgb_led.off()
    sys.exit()
