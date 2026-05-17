import board
import neopixel
import time

# --- Configuratie ---
LED_PIN = board.MOSI         # GPIO 10 (Pin 19)
NUM_LEDS = 60                # Aantal leds op jouw strip
BRIGHTNESS = 0.2             # Helderheid (0.0 tot 1.0) - Denk aan de stroom!

# Initialiseer de strip via SPI
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=BRIGHTNESS, auto_write=False)

# --- Kleurendefinities (R, G, B) ---
KLEUR_VAL = (0, 0, 255)      # Blauw voor het vallende ledje
KLEUR_STAPEL = (255, 255, 255) # Wit voor de gestapelde leds
KLEUR_ACHTERGROND = (0, 0, 0) # Uit

def stapel_effect(snelheid_val):
    # Begin met een lege strip
    pixels.fill(KLEUR_ACHTERGROND)
    pixels.show()
    
    # Buitenste loop: 'i' is het aantal leds dat al op de stapel ligt
    for i in range(NUM_LEDS):
        
        # Bepaal het eindpunt voor dit vallende ledje
        # (Het moet stoppen vóór de leds die er al liggen)
        eindpunt = NUM_LEDS - i
        
        # Binnenste loop: het ledje laten 'vallen'
        for j in range(eindpunt):
            # Teken het vallende ledje op de huidige positie
            pixels[j] = KLEUR_VAL
            
            # Haal het ledje op de vorige positie weg (indien niet de eerste)
            if j > 0:
                pixels[j-1] = KLEUR_ACHTERGROND
                
            # Laat de wijziging zien
            pixels.show()
            
            # Wacht even voor de animatiesnelheid
            time.sleep(snelheid_val)
            
        # Het ledje heeft zijn eindpunt bereikt en wordt onderdeel van de stapel
        # We geven het de stapelkleur
        pixels[eindpunt - 1] = KLEUR_STAPEL
        pixels.show()

    # Wacht even als de strip vol is
    time.sleep(2)
    print("Strip is vol, herstarten...")

# --- Hoofdprogramma ---
try:
    print(f"Stapel-effect gestart voor {NUM_LEDS} leds op GPIO 10...")
    print("Druk op Ctrl+C om te stoppen.")
    
    while True:
        # Voer het effect uit. 
        # Hoe lager het getal (bijv. 0.005), hoe sneller het valt.
        # Bij 60 leds moet het niet te traag vallen, anders duurt het lang.
        stapel_effect(0.01) 

except KeyboardInterrupt:
    # Netjes afsluiten: alle leds uit
    pixels.fill((0, 0, 0))
    pixels.show()
    print("\nProgramma gestopt.")