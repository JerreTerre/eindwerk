import serial
from RPLCD.i2c import CharLCD
from gpiozero import Motor, AngularServo, RGBLED
from time import sleep
import sys
import threading
import os

rgb_led = RGBLED(red=19, green=13, blue=26)
motor = Motor(forward=23, backward=24)
servo = AngularServo(17, initial_angle=90, min_angle=0, max_angle=180, min_pulse_width=7/10000, max_pulse_width=27/10000)

lcd = CharLCD(i2c_expander='PCF8574', address=0x3f, port=1,
              cols=16, rows=2, dotsize=8, charmap='A02',
              auto_linebreaks=False, backlight_enabled=True)

Duty_cycle = 0
hoek = 90
r=0
k=0
kleur="red"
frequentie=1
serialPort = serial.Serial(port='/dev/ttyAMA0', baudrate=9600, timeout=0, parity=serial.PARITY_EVEN, stopbits=1)
size = 1024
tijdaan=Duty_cycle/100/frequentie       
tijduit=(100-Duty_cycle)/100/frequentie
def LED():
    global Duty_cycle,kleur
    while True:
        if Duty_cycle == 0:
            kleur="blue"
            rgb_led.blue=1
            rgb_led.red=0
            rgb_led.green=0            
        elif Duty_cycle ==-20:
            kleur="red"
            rgb_led.red=1
            rgb_led.green=0
            rgb_led.blue=0
        elif Duty_cycle==100:
            if Duty_cycle>100:
                Duty_cycle=100
            kleur="wit"
            rgb_led.color=(1,1,1)    
        else:
            rgb_led.red=0
            rgb_led.blue=0
            rgb_led.green=(Duty_cycle/100)
            kleur="green"


def DCmotor(data):
    global Duty_cycle
    if data == b'B\xa1':
        Duty_cycle -= 20
        if Duty_cycle <-20:
            Duty_cycle = -20
        sleep(0.2)
    elif data == b'F\xa3':
        Duty_cycle += 20
        if Duty_cycle > 100:
            Duty_cycle = 100
        sleep(0.2)

    if (Duty_cycle>0):
         motor.forward(Duty_cycle/100)
    elif (Duty_cycle<0):
         motor.backward(abs(Duty_cycle)/100)     
    else:
        motor.stop()
def LCD():
    if (teller<=30):
        teller+=1
    elif (teller==30):
        teller=30

    else:
        teller=1
        lcd.cursor_pos = (1, 0)
def richting(data):
    global hoek
    if data == b'R\xa9':  
            hoek -= 18
            hoek = max(hoek, 0)
            servo.angle = hoek
            sleep(0.2)
    elif data == b'L\xa6':  
            hoek += 18
            hoek = min(hoek, 180)
            servo.angle = hoek
            sleep(0.2)
def LCD():
    global kleur,Duty_cycle,k,r
    while True:
        print('test')
        lcd.clear()
        lcd.cursor_pos = (r, k)
        lcd.write_string(kleur)
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"LED PWM:{Duty_cycle}%")
        k+=1
        sleep(1)
        if k==16:
            k=0
try:
    LCD_Thread=threading.Thread(target=LCD)
    LCD_Thread.daemon=True
    LCD_Thread.start()
    LED_thread = threading.Thread(target=LED)
    LED_thread.daemon = True
    LED_thread.start()

    while True:
        data = serialPort.readline(size).strip()   
        os.system('clear')
        print(f"Motor: {Duty_cycle}%, Kleur: {kleur},Servo: {hoek}")

        if data:
            DCmotor(data)
            richting(data)

        

except KeyboardInterrupt:
    motor.off()
    rgb_led.off()
    lcd.clear() 
    sys.exit()
