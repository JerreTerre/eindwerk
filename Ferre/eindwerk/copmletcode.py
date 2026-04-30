from gpiozero import Button
from adafruit_servokit import ServoKit
from time import sleep
import threading
import sys


SENSOR_PIN = 9
SWITCH_PIN = 6       # knop voor servo 3
MODE1_PIN = 22       # rocker stand 1
MODE2_PIN = 27       # rocker stand 2

kit = ServoKit(channels=16)

SERVO_1 = 0
SERVO_2 = 1
SERVO_3 = 2


sensor = Button(SENSOR_PIN, pull_up=False, bounce_time=0.1)
switch = Button(SWITCH_PIN, pull_up=False, bounce_time=0.1)
switch1 = Button(MODE1_PIN, pull_up=False, bounce_time=0.1)
switch2 = Button(MODE2_PIN, pull_up=False, bounce_time=0.1)


mode = 0


def update_mode():
    global mode
    if switch1.is_pressed:
        mode = 1
        print("1")
        
    elif switch2.is_pressed:
        mode = 2
        print("2")
    else:
        mode = 0


def set_servo(channel, angle):
    kit.servo[channel].angle = angle


def sensor_detected():
    if mode == 2:
        set_servo(SERVO_1, 90)
        

def sensor_undetected():
    if mode == 2:
        set_servo(SERVO_1, 0)
        

def switch_pressed():
    if mode == 2:
        set_servo(SERVO_2, 0)
    elif mode==1:
        set_servo(SERVO_3,35)

def switch_released():
    if mode == 2:
        set_servo(SERVO_2, 110)
    elif mode==1:
        set_servo(SERVO_3,90)


def servoklep():
    while True:

            sleep(0.2)


try:
    # Thread starten
    servo_thread = threading.Thread(target=servoklep, daemon=True)
    servo_thread.start()

    # Events koppelen
    sensor.when_pressed = sensor_detected
    sensor.when_released = sensor_undetected

    switch.when_pressed = switch_pressed
    switch.when_released = switch_released

    # Startpositie
    set_servo(SERVO_1, 0)
    set_servo(SERVO_2, 110)
    set_servo(SERVO_3, 90)

    print("Programma gestart")

    while True:
        update_mode()
        sleep(0.1)

except KeyboardInterrupt:
    print("\nProgramma gestopt")

finally:
    sensor.close()
    switch.close()
    switch1.close()
    switch2.close()

    kit.servo[SERVO_1].angle = None
    kit.servo[SERVO_2].angle = None
    kit.servo[SERVO_3].angle = None

    sys.exit()
