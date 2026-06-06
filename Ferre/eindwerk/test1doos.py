import os
import sys
import time
from time import sleep
from signal import pause

import board
import neopixel
from adafruit_servokit import ServoKit
from gpiozero import Button, OutputDevice

# --- Configuratie Sensor en Solenoid ---
SENSOR_PIN = 23  # BCM pin
sensor = Button(SENSOR_PIN, pull_up=False)
solenoid = OutputDevice(18, active_high=False, initial_value=False)

# --- Configuratie Schakelaar en Servo ---
SCHAKELAAR_PIN = 6  # BCM pin waar de schakelaar op zit
schakelaar = Button(SCHAKELAAR_PIN, pull_up=False, bounce_time=0.05)

# Initialiseer de PCA9685 (16 kanalen)
kit = ServoKit(channels=16)

# --- Configuratie LED Strip ---
LED_PIN = board.MOSI          # GPIO 10 (Pin 19)
NUM_LEDS = 60                 # Aantal leds op de strip
BRIGHTNESS = 0.2              # Helderheid (0.0 tot 1.0)

# Initialiseer de strip via SPI
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=BRIGHTNESS, auto_write=False)

# --- Kleurendefinities (R, G, B) ---
KLEUR_ACHTERGROND = (0, 0, 0)
KLEUREN = [
    (255, 0, 0),      # Rood
    (0, 255, 0),      # Groen
    (0, 0, 255),      # Blauw
    (255, 255, 0),    # Geel
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyaan
]

previous_sensor_state = None
previous_servo_angle = None
led_count = 0  # Aantal leds dat aangezet is

try:
    print("Systeem gestart...")
    print(f"LED-strip actief op {NUM_LEDS} leds (GPIO 10)")
    print(f"Servo luistert naar schakelaar op GPIO {SCHAKELAAR_PIN}")
    print("Druk op Ctrl+C om te stoppen.")
    
    pixels.fill(KLEUR_ACHTERGROND)
    pixels.show()
    
    # --- Hoofd-lus ---
    while True:
        
        # --- Deel 1: Servo & Schakelaar sturing ---
        if schakelaar.is_pressed:
            # Schakelaar staat AAN (ingedrukt) -> Servo naar 10 graden
            target_angle = 10
        else:
            # Schakelaar staat AF (niet ingedrukt) -> Servo naar 180 graden
            target_angle = 180

        # Alleen de servo aansturen als de hoek daadwerkelijk moet veranderen
        if target_angle != previous_servo_angle:
            kit.servo[14].angle = target_angle
            print(f"Schakelaar status veranderd: Servo naar {target_angle} graden")
            previous_servo_angle = target_angle


        # --- Deel 2: Sensor, Solenoid en LEDs sturing ---
        if sensor.is_pressed:
            if previous_sensor_state != True:
                print("Sensor detecteert - Solenoid AAN, 10 leds toegevoegd")
                previous_sensor_state = True
                
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
            if previous_sensor_state != False:
                print("Sensor detecteert niets - Solenoid UIT")
                previous_sensor_state = False
            solenoid.off()
        
        sleep(0.1)

except KeyboardInterrupt:
    print("\nProgramma handmatig gestopt.")

finally:
    # Zorg dat alles netjes uitschakelt bij het afsluiten
    solenoid.off()
    pixels.fill((0, 0, 0))
    pixels.show()
    print("Schoonmaken voltooid. Alles staat uit.")