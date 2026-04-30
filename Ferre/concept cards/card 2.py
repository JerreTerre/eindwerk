from gpiozero import RGBLED , Button , Motor
from time import sleep
import sys
import os

rgb_led = RGBLED(red=19, green=26, blue=13)
button1 = Button(6,pull_up=False)
button2 = Button(5,pull_up=False)
motor = Motor(forward=23, backward=24)
Duty_cycle=0


try:
    while True:
        tijdaan=abs(Duty_cycle)/100
        tijduit=(100-abs(Duty_cycle))/100
        if (Duty_cycle>0):
            rgb_led.color = (1, 0, 0 )
            rgb_led.on()
            rgb_led.color = (1, 0, 0)
            sleep(tijdaan)
            rgb_led.off()
            sleep(tijduit)
        elif(Duty_cycle<0):
            rgb_led.color = (0, 1, 0)
            rgb_led.on()
            rgb_led.color = (0, 1, 0)
            sleep(tijdaan)
            rgb_led.off()
            sleep(tijduit)
            
        else:
            rgb_led.color = (0, 0, 1)
            sleep(tijdaan)

        if (Duty_cycle>0):
            motor.forward(Duty_cycle/100)
        elif (Duty_cycle<0):
            motor.backward(abs(Duty_cycle)/100)     #pakt de absolute waarde van -10 tot -100
        else:
            motor.stop()

        if button1.is_pressed:
            Duty_cycle+=10
            if Duty_cycle>100:
                Duty_cycle=100
            os.system('clear')
            print("duty=", Duty_cycle,"%")
            sleep(0.5)
            
        while button1.is_pressed:      
            pass                     
        sleep(0.05)                
    
        if button2.is_pressed:
            Duty_cycle-=10

            if Duty_cycle<-100:
                Duty_cycle=-100    
            os.system('clear')
            print("duty=", Duty_cycle,"%")
            sleep(0.5)

        while button2.is_pressed:      
            pass                     
        sleep(0.05)                
        



except KeyboardInterrupt:  # Als "ctrl+c" wordt gedrukt
    motor.stop()
    sys.exit()