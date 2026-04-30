from RPLCD.i2c import CharLCD 
from gpiozero import RGBLED , Button
from time import sleep
import os
import sys
import threading
import time
rgb_led = RGBLED(red=26, green=19, blue=13)
button1 = Button(5, pull_up=False, bounce_time=0.05)  
lcd = CharLCD(i2c_expander='PCF8574', address=0x3f, port=1,
			  cols=16, rows=2, dotsize=8, charmap='A02',
			  auto_linebreaks=False, backlight_enabled=True)

kleur="red"
teller=1
k=0
r=0
def LED():
	global teller
	global kleur
	while True:
		os.system('clear')
		rgb_led.color = (0,1,0)
		kleur="red"
		print("red")
		sleep(4)
		os.system('clear')
		lcd.clear()	
		while teller==30:
			pass
		rgb_led.color = (1,0,0)
		kleur="green"
		print("green")
		sleep(4)
		os.system('clear')
		lcd.clear()	
		while teller==30:
			pass
		rgb_led.color = (0,0,1)
		kleur="blue"
		print("blue")
		sleep(4)
		os.system('clear')
		lcd.clear()	
		while teller==30:
			pass
def interupt():
	global teller
	if (teller<=30):
		teller+=1
	elif (teller==30):
		teller=30

	else:
		teller=1
		lcd.cursor_pos = (1, 0)

try:
	LED_thread = threading.Thread(target=LED)
	LED_thread.daemon = True
	LED_thread.start()
	button1.when_pressed = interupt
	while True:
		lcd.cursor_pos = (r, k)
		lcd.write_string(kleur)
		lcd.cursor_pos = (1, 0)
		lcd.write_string(str(teller))
		sleep(0.5)
		while teller==30:
				lcd.clear()
				lcd.cursor_pos = (r, k)
				lcd.write_string(kleur)
				lcd.cursor_pos = (1, 0)
				lcd.write_string(str(teller))
				k+=1
				sleep(0.5)
				if k==16:
					k=0
				lcd.cursor_pos = (r, k)
				lcd.write_string(kleur)
				lcd.cursor_pos = (1, 0)
				lcd.write_string(str(teller))
		if teller>30:
			teller=1
			k=0
			lcd.clear()
		
			
		



except KeyboardInterrupt:
	rgb_led.off()
	sys.exit()
	lcd.clear()	
