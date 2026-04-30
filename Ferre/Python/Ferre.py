import spidev
from time import sleep
import sys
import smbus
import os

bus=smbus.SMBus(1)
spi= spidev.SpiDev()
spi.open(0,0) #SPI bus openen
spi.max_speed_hz = 5000 #Moet, anders werkt SPI niet correct

DEVICE = 0x20
IODIRA = 0x00
GPIOA = 0x12
bus.write_byte_data(DEVICE,IODIRA,0x00)
teller=0
	   
try:
	
	while True:
		os.system('clear')
		MySwitch = bus.read_byte_data(DEVICE,GPIOA)
		if MySwitch & 0b00010000 == 0b00010000:
			teller+=1
			sleep(0.5)
			if teller>4:
				teller=0
		if (teller==1):
			bus.write_byte_data(DEVICE,GPIOA,0b01000000)
			print("rood")	
		elif (teller==2):
			bus.write_byte_data(DEVICE,GPIOA,0b10000000)
			print("groen")	
		elif (teller==3):
			bus.write_byte_data(DEVICE,GPIOA,0b00100000)
			print("blauw")	
		elif (teller==4):
			bus.write_byte_data(DEVICE,GPIOA,0b11100000) 
			print("wit")  
		else:
			print("uit")
			bus.write_byte_data(DEVICE,GPIOA,0b00000000)
			  

except KeyboardInterrupt:
	spi.close()
	sys.exit(0)
	bus.write_byte_data(DEVICE,GPIOA,0x00)              #alle pinnen laag maken
	bus.write_byte_data(DEVICE,IODIRA,0x00)