from RPLCD.i2c import CharLCD
import time

lcd = CharLCD(i2c_expander='PCF8574', address=0x3f, port=1,
			  cols=16, rows=2, dotsize=8, charmap='A02',
			  auto_linebreaks=False, backlight_enabled=True)

kolom = 0
row = 0
text="Hello, RPLCD!"
while True:
	lcd.cursor_pos = (row, kolom)
	lcd.write_string("Hello, RPLCD!")
	print(text[0:16])
	time.sleep(0.5)
	lcd.clear()
	
	kolom += 1
	if kolom >= 16:
		kolom = 0
		row += 1
	
	if row >= 2:
		row = 0
