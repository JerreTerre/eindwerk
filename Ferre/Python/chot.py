from gpiozero import Button,AngularServo,RGBLED
from time import sleep
import os
import sys
import threading

rgb_led=RGBLED(red=19,green=26,blue=13)
drukknop1 = Button(6, pull_up=False,bounce_time=0.3)
drukknop2= Button(5, pull_up=False,bounce_time=0.3)
servo = AngularServo(17, initial_angle=0, min_angle=0, max_angle=180, min_pulse_width=7/10000, max_pulse_width=27/10000)
Duty_cycle=0
angle=180
schot=0
frequentie=1
def RGBLED():
	rgb_led.color=(1,0,0)
	sleep(frequentie)
	rgb_led.color=(0,1,0)
	sleep(frequentie)
	rgb_led.color=(0,0,1)
	sleep(frequentie)
try:
	RGBLED=threading.Thread(target=RGBLED)
	RGBLED.daemon=True
	RGBLED.start()
	while True:
		if drukknop1.is_pressed:
			schot+=10
			if schot>100:
				schot=100
			angle+=18
			if angle>180:
				angle=180
			servo.angle=angle
			Duty_cycle+=10
			if Duty_cycle>100:
				Duty_cycle=100
		os.system('clear')
		print("Duty Cycle=",Duty_cycle,"%")
		print("schot ",schot,"% Servo hoek ",angle,"°")
		if drukknop2.is_pressed:
			schot-=10
			if schot<0:
				schot=0
			angle-=18
			if angle<0:
				angle=0
			servo.angle=angle
			Duty_cycle-=10
			if Duty_cycle<0:
				Duty_cycle=0
			os.system('clear')
			print("Duty Cycle=",Duty_cycle,"%")
			print("schot ",schot,"% Servo hoek ",angle,"°")			

except KeyboardInterrupt:
	sys.exit()
	rgb_led.off()