import spidev
from time import sleep
import sys
import smbus

bus=smbus.SMBus(1)
spi= spidev.SpiDev()
spi.open(0,0) #SPI bus openen
spi.max_speed_hz = 5000 #Moet, anders werkt SPI niet correct

DEVICE = 0x20
IODIRA = 0x00
GPIOA = 0x12
                                                        #I2C bust instellen
bus.write_byte_data(DEVICE,IODIRA,0x00)

try:
    while True:
        bus.write_byte_data(DEVICE,GPIOA,0b00000000)
        chan = 0 #Keuze van kanaal
        result = spi.xfer2([1,(8 + chan)<<4,0])# Stuur commando: startbit + kanaal + dummy byte

        adcValue = (((result[1]&3)<<8)+result[2]) # Combineer 2 bits (result[1]) + 8 bits (result[2]) → 10-bit waarde (0–1023)
        print(adcValue)
        if adcValue > 511:
            bus.write_byte_data(DEVICE,GPIOA,0b10000000)    #kleur 1 sturen dus GPIOA7 hoog maken en de rest laag maken
        sleep(0.5)

except KeyboardInterrupt:
    spi.close()
    sys.exit(0)
    bus.write_byte_data(DEVICE,GPIOA,0x00)              #alle pinnen laag maken
    bus.write_byte_data(DEVICE,IODIRA,0x00)