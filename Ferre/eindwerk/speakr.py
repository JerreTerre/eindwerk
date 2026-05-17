import pygame
import time
import os

def speel_succes_geluid():
    # Het exacte pad naar jouw bestand
    bestands_pad = "/home/pi/Ferre/eindwerk/geluid/insomnia.mp3"
    
    # Controleer of het bestand echt op die plek staat
    if not os.path.exists(bestands_pad):
        print(f"Fout: Bestand niet gevonden op {bestands_pad}")
        return

    try:
        # Initialiseer de mixer
        pygame.mixer.init()
        pygame.mixer.music.load(bestands_pad)
        
        print("Actie geslaagd! Geluid wordt afgespeeld...")
        pygame.mixer.music.play()

        # Wacht tot het geluid klaar is (anders stopt het script te vroeg)
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Er ging iets mis bij het afspelen: {e}")
    finally:
        # Netjes afsluiten om bronnen vrij te geven
        pygame.mixer.quit()

# --- Voorbeeld van hoe je dit gebruikt in je eindwerk ---

def check_status():
    # Hier komt jouw logica
    # Bijvoorbeeld: als een sensor iets meet of een berekening klaar is
    succes = True 

    if succes:
        speel_succes_geluid()

if __name__ == "__main__":
    check_status()