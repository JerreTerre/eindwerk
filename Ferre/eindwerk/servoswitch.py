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
        kit.servo[0].angle=10
        print("90")
        sleep(1)
        kit.servo[0].angle=110

        print("0")
        sleep(1)

        

        
        
        
except KeyboardInterrupt:
    sys.exit()
