import serial
from RPLCD.i2c import CharLCD 
import os
import threading 

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)  
lcd = CharLCD(i2c_expander='PCF8574', address=0x3f, port=1,
			  cols=16, rows=2, dotsize=8, charmap='A02',
			  auto_linebreaks=True, backlight_enabled=True)
size = 1024  
 

def waitRcvLn():
    str_data = ser.readline()  
    if str_data:
        return str_data.decode().strip()  

try:
    os.system('clear')
    while True:
        recvStr = waitRcvLn()
        if recvStr:
            os.system('clear')  
            print(recvStr)
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(str(recvStr))
        

except KeyboardInterrupt:
    ser.close()  
    lcd.clear()
    
