import serial
from RPLCD.i2c import CharLCD
from gpiozero import Motor, AngularServo, RGBLED
from time import sleep
import sys
import threading

rgb_led = RGBLED(red=19, green=13, blue=26)
motor = Motor(forward=23, backward=24)
servo = AngularServo(17, initial_angle=90, min_angle=0, max_angle=180, min_pulse_width=7/10000, max_pulse_width=27/10000)

lcd = CharLCD(i2c_expander='PCF8574', address=0x3f, port=1,
              cols=16, rows=2, dotsize=8, charmap='A02',
              auto_linebreaks=True, backlight_enabled=True)

Duty_cycle = 0
hoek = 90

serialPort = serial.Serial(port='/dev/ttyAMA0', baudrate=9600, timeout=0, parity=serial.PARITY_EVEN, stopbits=1)

size = 1024

def LED():
    global Duty_cycle
    while True:
        if Duty_cycle < 30:
            rgb_led.color = (0, 1, 0)
            sleep(0.5)
        elif Duty_cycle >= 30 and Duty_cycle < 75:
            rgb_led.color = (1, 0, 0)
            sleep(0.5)
        elif Duty_cycle >= 75:
            rgb_led.color = (0, 0, 1)
            sleep(0.5)

def DCmotor(data):
    global Duty_cycle
    if data == b'B\xa1':
        Duty_cycle -= 3
        if Duty_cycle==-20:
            motor.backward((abs(Duty_cycle)/100) )
    elif data == b'F\xa3':
        Duty_cycle += 2
        motor.forward(Duty_cycle / 100)
        if Duty_cycle > 100:
            Duty_cycle = 100
    

def richting(data):
    global hoek
    if data == b'R\xa9':  
        for i in range(10):
            hoek -= 1
            hoek = max(hoek, 0)
            servo.angle = hoek
            sleep(0.01)
    elif data == b'L\xa6':  
        for i in range(10):
            hoek += 1
            hoek = min(hoek, 180)
            servo.angle = hoek
            sleep(0.01)

try:
    LED_thread = threading.Thread(target=LED)
    LED_thread.daemon = True
    LED_thread.start()

    while True:
        data = serialPort.readline(size).strip()   

        if data:
            DCmotor(data)
            richting(data)

        lcd.cursor_pos = (0, 0)
        lcd.write_string("PWM:" + str(Duty_cycle) + "% Hoek: " + str(int(hoek)) + "° ")

        lcd.cursor_pos = (1, 0)
        if hoek > 90:
            lcd.write_string("Richting: Links  ")
        elif hoek < 90:
            lcd.write_string("Richting: Rechts ")
        else:
            lcd.write_string("Richting: Recht  ")

except KeyboardInterrupt:
    motor.off()
    rgb_led.off()
    lcd.clear() 
    sys.exit()
