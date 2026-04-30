from gpiozero import LED
import time
import board
import busio
import adafruit_bmp280
import os

i2c = busio.I2C(board.SCL, board.SDA)
fan = LED(26)
bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
x=bmp.temperature
w=19
Y=None
def ventilator():
    global Y
    if x>(w+1):
        fan.on()
        Y=1

    elif x<(w-1):
        fan.off()
        Y=0
    else:
        print("warm genoeg")


try:
    while True:
        os.system('clear')
        ventilator()
        print("Temperatuur: {:.2f} °C".format(bmp.temperature))
        print("Y=",Y)
        print("Gewenste temp",w)
        print("----------")
        time.sleep(1)
except KeyboardInterrupt:
    fan.off()
    print("\nPogramma stop")

