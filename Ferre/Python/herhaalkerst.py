from gpiozero import Button, AngularServo, RGBLED, Motor
from time import sleep
import os
import sys
import threading

# Apparaten instellen
rgb_led = RGBLED(red=19, green=26, blue=11)
button1 = Button(6, pull_up=False, bounce_time=0.05)  # Voor wachtwoordcontrole en auto passage
button2 = Button(5, pull_up=False, bounce_time=0.05)  # Voor reset van pogingen
motor = Motor(forward=23, backward=24)
servo = AngularServo(17, initial_angle=0, min_angle=0, max_angle=90)

# Variabelen
Totaal = 0  # De teller voor auto's die passeren
hoek_array = [0, 18, 36, 54, 72, 90]
pogingen_over = 3
code_correct = False
code = None  # Wachtwoord wordt ingesteld in de while-lus

def LEDRED():
    """Knipper rood licht."""
    while True:
        rgb_led.red = 1
        sleep(0.5)
        rgb_led.red = 0
        sleep(0.5)

def Motordraaien():
    """Draai de motor tijdens de slagboomactie."""
    motor.forward(0.5)
    sleep(5)
    motor.stop()
    sleep(5)  # Wacht 5 seconden
    motor.backward(0.5)
    sleep(5)
    motor.stop()

def slagboom():
    """Beheer de slagboom en LED-status."""
    global Totaal
    motor_thread = threading.Thread(target=Motordraaien)
    motor_thread.start()  # Start de motoractie parallel aan de slagboom

    # Start rode LED knipperen
    red_thread = threading.Thread(target=LEDRED)
    red_thread.daemon = True
    red_thread.start()

    # Open de slagboom
    for hoek in hoek_array:
        servo.angle = hoek
        # Pulsbreedte berekenen
        pulse_width = servo.pulse_width
        print(f"Servo-hoek: {hoek} graden, Pulsbreedte: {pulse_width * 1000:.2f} ms")
        sleep(0.87)
        os.system('clear')

    # Zet de LED op groen als de slagboom helemaal open is
    rgb_led.red = 0  # Stop rood knipperen
    rgb_led.green = 1
    sleep(3)  # Houd de slagboom 5 seconden open

    # Zet de LED op oranje 2 seconden voordat de slagboom naar beneden gaat
    rgb_led.green = 1
    rgb_led.red = 1
    rgb_led.blue = 0  # Oranje (rood + blauw)
    print("LED is oranje. Slagboom gaat bijna dicht.")
    sleep(2)

    # Sluit de slagboom
    rgb_led.green = 0  # Stop oranje
    rgb_led.red = 1  # Terug naar rood knipperen
    for hoek in reversed(hoek_array):
        servo.angle = hoek
        # Pulsbreedte berekenen
        pulse_width = servo.pulse_width
        print(f"Servo-hoek: {hoek} graden, Pulsbreedte: {pulse_width * 1000:.2f} ms")
        sleep(0.87)
        os.system('clear')

    # Verhoog de teller nadat de slagboom naar beneden is
    Totaal += 1
    print(f"Aantal auto's die gepasseerd zijn: {Totaal}")

def wachtwoordcontrole():
    """Controleer het wachtwoord."""
    global pogingen_over, code_correct
    for _ in range(pogingen_over):
        ingevoerde_code = input("Voer het wachtwoord in: ").strip()
        if ingevoerde_code == code:
            print("Correct wachtwoord! Slagboom wordt geactiveerd.")
            code_correct = True
            slagboom()
            return
        else:
            pogingen_over -= 1
            print(f"Fout wachtwoord! Pogingen over: {pogingen_over}")

    print("Geen pogingen meer over. Druk op knop 2 om te resetten.")

def reset_pogingen():
    """Reset het aantal pogingen."""
    global pogingen_over, code_correct
    print("Pogingen worden gereset...")
    pogingen_over = 3
    code_correct = False
    print("Je kunt opnieuw proberen het wachtwoord in te voeren.")
    wachtwoordcontrole()

# Hoofdlogica
try:    
    button1.when_pressed = wachtwoordcontrole  # Start de wachtwoordcontrole als knop 1 wordt ingedrukt
    button2.when_pressed = reset_pogingen  # Reset pogingen als knop 2 wordt ingedrukt
    while True:
        # Vraag om het wachtwoord als het nog niet is ingesteld
        if code is None:
            code = input("Stel een wachtwoord in voor het codeklavier: ").strip()
            print("Wachtwoord is ingesteld. Gebruik knop 1 om toegang te krijgen.")

except KeyboardInterrupt:
    print("\nProgramma beëindigd.")
    motor.off()
    rgb_led.off()
    sys.exit()
