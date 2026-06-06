from gpiozero import AngularServo, Button
from time import sleep
import os
import sys
import threading
from adafruit_servokit import ServoKit

button1 = Button(6, pull_up=False,bounce_time=0.05)

kit = ServoKit(channels=16)







try:
    

    while True:
        kit.servo[9].angle = 160
        kit.servo[13].angle = 160
        kit.servo[5].angle = 160
        kit.servo[1].angle = 160
        print("160")
        sleep(1)
        kit.servo[9].angle = 0
        kit.servo[13].angle = 0
        kit.servo[5].angle = 0
        kit.servo[1].angle = 0
        print("0")
        sleep(1)

        

        
        
        
except KeyboardInterrupt:
    sys.exit()
