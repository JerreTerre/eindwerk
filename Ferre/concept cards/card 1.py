from gpiozero import LED , Button               
from time import sleep
import sys
button1 = Button(6,pull_up=False)
button2 = Button(5,pull_up=False)
LED=LED(13)
duty_cycle=50
frequentie=1
teller=0
try:
    while True:
            tijdaan=duty_cycle/100/frequentie       # de tijd dat LED aanstaat Bv:50/100/1=5ms
            tijduit=(100-duty_cycle)/100/frequentie

            LED.on()
            sleep(tijdaan)
            LED.off()
            sleep(tijduit)
            if button1.is_pressed:
                teller+=1                   #per keer dat de drukknop wordt in gedrukt teller+1
                frequentie = teller * 2     #frequentie=1 *2 =2hz en dan terug *2
                sleep(0.5)
                if frequentie>20:           #wanneer frequentie > 20 teller=0 en freq=1hz
                    teller=0
                    frequentie=1
                print("frequentie= ",frequentie,"Hz")     #zet de frequentie in de shell

            if button2.is_pressed:
                duty_cycle+=10              #+10% bij duty_cycle
                sleep(0.5)
                if duty_cycle>100:
                    duty_cycle=10
                print("duty=", duty_cycle,"%")



except KeyboardInterrupt:           
   LED.off()