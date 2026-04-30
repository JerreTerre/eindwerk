from gpiozero import RGBLED
from time import sleep
import sys

# Initialiseer de RGB LED (rood, groen, blauw) op pinnen GPIO22 GPIO21 en GPIO20
rgb_led = RGBLED(red=16, green=19, blue=13)

try:
	while True:
		rgb_led.color = (1, 0, 0)  # Rood
		print("rood")
		sleep(1)

		rgb_led.color = (0, 1, 0)  # Groen
		print("groen")
		sleep(1)

		rgb_led.color = (0, 0, 1)  # Blauw
		print("blauw")
		sleep(1)

		rgb_led.color = (1, 1, 0)  # Geel
		print("geel")
		sleep(1)

		rgb_led.color = (0, 1, 1)  # Cyaan
		print("cyaan")
		sleep(1)

		rgb_led.color = (1, 0, 1)  # Magenta
		print("magenta")
		sleep(1)

		rgb_led.color = (0, 0, 0)  # Uit
		print("uit")
		sleep(1)
		for n in range(100):
			rgb_led.blue = (n/100)		#stuur een getal tussen 0 en 1 naar blue om de helderheid te bepalen
			sleep(0.1)

except KeyboardInterrupt:  # Als "ctrl+c" wordt gedrukt
	rgb_led.off()
	sys.exit()