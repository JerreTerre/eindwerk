from gpiozero import LED, Button
from time import sleep, time
import os

# GPIO Setup
led = LED(12)
button = Button(16, pull_up=False, bounce_time=0.05)


binary_string = ""  # Hier wordt de ontvangen binaire data opgeslagen
TIMEOUT = 2  # Tijd (seconden) voordat een zin als "compleet" wordt beschouwd

# Bitlengtes
EEN = 0.5
NUL = 0.2

def clear_screen():
    os.system('clear')  # Gebruik 'cls' op Windows

def binary_to_ascii(binary_string):
    """Converteert een binaire string naar ASCII-tekst."""
    ascii_string = ""
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            ascii_string += chr(int(byte, 2))
    return ascii_string

 

while True:
    try:
        clear_screen()
        print("Wil je verzenden of ontvangen?")
        mode = input("[V] Verzenden | [O] Ontvangen: ").lower()

        if mode == "v":
            test_str = input("Voer de zin in die je wilt verzenden: ")
            binary_data = ''.join(format(ord(c), '08b') for c in test_str)
            print(f"De string na binaire conversie: {binary_data}")

            for bit in binary_data:
                if bit == '1':
                    led.on()
                    sleep(EEN)
                else:
                    led.on()
                    sleep(NUL)
                led.off()
                sleep(NUL)  # Pauze tussen bits
                print(f"{bit} is verzonden")

            # LCD Weergave na verzenden
           
            print("\nZin succesvol verzonden!")
            sleep(2)  # Kleine pauze voordat het menu terugkomt

        elif mode == "o":
            binary_string = ""
            last_input_time = time()

            print("Ontvangst gestart... Druk op Ctrl+C om te stoppen.")

            while True:
                # Controleer of er een pauze in de invoer is
                if time() - last_input_time > TIMEOUT and binary_string:
                    ontvangen_woord = binary_to_ascii(binary_string)
                    print(f"\n Volledig ontvangen zin: {ontvangen_woord}")
                   
                    print("\nWachten op nieuwe zin...\n")
                    sleep(2)  # Kleine pauze voordat het menu terugkomt
                    break  # Terug naar het menu

                # Wacht op knopdruk
                button.wait_for_press()
                start_time = time()

                # Wachten tot de knop wordt losgelaten
                button.wait_for_release()
                duration = time() - start_time
                last_input_time = time()  # Reset de timer

                # Bepaal of het een '1' of '0' is
                if duration >= EEN:
                    binary_string += "1"
                elif duration >= NUL:
                    binary_string += "0"
                else:
                    print("Te korte druk, genegeerd.")

                clear_screen()
                ontvangen_woord = binary_to_ascii(binary_string)
                print(f" Huidige binaire string: {binary_string}")
                print(f" Huidige ontvangen tekst: {ontvangen_woord}")  # LIVE in de shell tonen

        else:
            print("Ongeldige invoer, probeer opnieuw!")

    except KeyboardInterrupt:
        led.off()
     
        print("\nProgramma gestopt door gebruiker.")
        break