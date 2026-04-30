from gpiozero import Button
from adafruit_servokit import ServoKit
from time import sleep

# --- PIN DEFINITIES ---
switch1 = Button(22, pull_up=False, bounce_time=0.1)   # Mode 1
switch2 = Button(27, pull_up=False, bounce_time=0.1)   # Mode 2
sensor  = Button(17, pull_up=False, bounce_time=0.1)   # Sensor voor servo 1
tuimel  = Button(6,  pull_up=False, bounce_time=0.1)   # Schakelaar voor servo 2

# --- SERVO KIT ---
kit = ServoKit(channels=16)

SERVO_1 = 0
SERVO_2 = 1
SERVO_3 = 2

mode = 0


# --- MODE UPDATE ---
def update_mode():
    global mode
    if switch1.is_pressed:
        mode = 1
        print("MODE 1 actief")
    elif switch2.is_pressed:
        mode = 2
        print("MODE 2 actief")
    else:
        mode = 0


# --- SERVO FUNCTIES ---
def set_servo(channel, angle):
    kit.servo[channel].angle = angle


# --- SENSOR EVENTS ---
def sensor_pressed():
    if mode == 1:
        set_servo(SERVO_2, 90)

def sensor_released():
    if mode == 1:
        set_servo(SERVO_2, 0)


# --- TUIMELSCHAKELAAR EVENTS ---
def tuimel_pressed():
    if mode == 2:
        set_servo(SERVO_3, 100)
    elif mode == 1:
        set_servo(SERVO_1, 0)

def tuimel_released():
    if mode == 2:
        set_servo(SERVO_3, 0)
    elif mode == 1:
        set_servo(SERVO_1, 70)


# --- EVENT KOPPELING ---
sensor.when_pressed = sensor_pressed
sensor.when_released = sensor_released

tuimel.when_pressed = tuimel_pressed
tuimel.when_released = tuimel_released


# --- START ---
print("Programma gestart")
set_servo(SERVO_1, 70)
set_servo(SERVO_2, 0)
set_servo(SERVO_3, 0)

try:
    while True:
        update_mode()
        sleep(0.1)

except KeyboardInterrupt:
    print("Programma gestopt")
    set_servo(SERVO_1, None)
    set_servo(SERVO_2, None)
    set_servo(SERVO_3, None)
