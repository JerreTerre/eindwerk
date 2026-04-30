import random
import serial
from RPLCD.i2c import CharLCD
from gpiozero import Motor, AngularServo, RGBLED, Button
from time import sleep
import sys
import threading
import os

rgb_led = RGBLED(red=19, green=13, blue=20)
motor = Motor(forward=23, backward=24)
servo = AngularServo(17, initial_angle=0, min_angle=0, max_angle=180, min_pulse_width=7/10000, max_pulse_width=27/10000)
lcd = CharLCD(i2c_expander='PCF8574', address=0x3f, port=1, cols=16, rows=2, dotsize=8, charmap='A02', auto_linebreaks=True, backlight_enabled=True)
serialPort = serial.Serial(port='/dev/ttyAMA0', baudrate=9600, timeout=0, parity=serial.PARITY_EVEN, stopbits=1)
button1 = Button(6, pull_up=False, bounce_time=0.05)

hoeken = list(range(1, 181))
Duty_cycle = 0
goedgeraden = 0
timer = 0
geraden = random.randint(1, 10)
randomgetal = random.randint(1, 10)

def led_cycle():
    while True:
        rgb_led.color = (1, 0, 0)
        sleep(1)
        rgb_led.color = (0, 1, 0)
        sleep(1)
        rgb_led.color = (0, 0, 1)
        sleep(1)

def drukknop1():
    global Duty_cycle, goedgeraden, timer, geraden, randomgetal
    Duty_cycle = 0
    goedgeraden = 0
    timer = 0
    geraden = random.randint(1, 10)
    randomgetal = random.randint(1, 10)
    servo.angle = 0  # Zet de servo op 0 als de knop wordt ingedrukt

def process_input(data):
    global geraden, randomgetal, timer, goedgeraden
    os.system('clear')
    print(f"Geraden: {geraden}, Randomgetal: {randomgetal}")
    
    if data.startswith(b'R'):
        print("Goed geraden!")
        goedgeraden += 1
        sleep(3)
        timer = 0
        geraden = random.randint(1, 10)
        randomgetal = random.randint(1, 10)
        servo.angle = 0  # Zet de servo op 0 als het getal is geraden
    elif data.startswith(b'B'):
        randomgetal -= 1
    elif data.startswith(b'F'):
        randomgetal += 1

def timer_function():
    global timer
    while True:
        timer += 0.1
        if timer >= 90:
            for speed in range(0, 101, 14):
                motor.forward(speed / 100)
                sleep(1)
        sleep(0.1)

def servootje():
    global hoek, hoeken
    for hoek in hoeken:
        servo.angle = hoek
        sleep(1)

try:
    servo_thread = threading.Thread(target=servootje, daemon=True)
    servo_thread.start()
    timer_thread = threading.Thread(target=timer_function, daemon=True)
    timer_thread.start()
    rgb_thread = threading.Thread(target=led_cycle, daemon=True)
    rgb_thread.start()
    button1.when_pressed = drukknop1   
    
    while True:
        data = serialPort.readline().strip()
        os.system('clear')
        print(f"Geraden: {geraden}, Randomgetal: {randomgetal}")
        
        if data:
            process_input(data)
            
        lcd.clear()
        lcd.write_string(f"Timer: {round(timer, 1)}s")
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"Geraden: {goedgeraden}")
        sleep(0.1)

except KeyboardInterrupt:
    motor.off()
    rgb_led.off()
    lcd.clear()
    sys.exit()
