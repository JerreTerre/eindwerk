from gpiozero import OutputDevice
from time import sleep
from gpiozero import Button
from signal import pause
import board
import neopixel
import time

# --- Configuratie Sensor en Solenoid ---
SENSOR_PIN = 15  # BCM pin

sensor = Button(SENSOR_PIN, pull_up=False)
solenoid = OutputDevice(4, active_high=False, initial_value=False)

# --- Configuratie LED Strip ---
LED_PIN = board.MOSI         # GPIO 10 (Pin 19)
NUM_LEDS = 60                # Aantal leds op jouw strip
BRIGHTNESS = 0.2             # Helderheid (0.0 tot 1.0) - Denk aan de stroom!

# Initialiseer de strip via SPI
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=BRIGHTNESS, auto_write=False)

# --- Kleurendefinities (R, G, B) ---
KLEUR_ACHTERGROND = (0, 0, 0) # Uit

# Array met kleuren (10 van elke kleur)
KLEUREN = [
    (255, 0, 0),      # Rood
    (0, 255, 0),      # Groen
    (0, 0, 255),      # Blauw
    (255, 255, 0),    # Geel
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyaan
]

previous_state = None
led_count = 0  # Aantal leds dat aangezet is

try:
    print(f"LED-strip gestart voor {NUM_LEDS} leds op GPIO 10...")
    print("Druk op Ctrl+C om te stoppen.")
    
    pixels.fill(KLEUR_ACHTERGROND)
    pixels.show()
    
    while True:
        if sensor.is_pressed:
            if previous_state != True:
                print(f"Sensor detecteerd - Solenoid AAN, 10 leds toegevoegd")
                previous_state = True
                
                # Voeg 10 leds toe met de huidige kleur
                kleur_index = (led_count // 10) % len(KLEUREN)
                kleur = KLEUREN[kleur_index]
                
                for i in range(10):
                    if led_count < NUM_LEDS:
                        pixels[led_count] = kleur
                        led_count += 1
                pixels.show()
            solenoid.on()
        else:
            if previous_state != False:
                print(f"Sensor detecteert niets - Solenoid UIT")
                previous_state = False
            solenoid.off()
        
        sleep(0.1)

except KeyboardInterrupt:
    print("Gestopt")
    solenoid.off()
    pixels.fill((0, 0, 0))
    pixels.show()