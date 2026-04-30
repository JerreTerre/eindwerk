from gpiozero import DistanceSensor
from time import sleep

# Definieer de sensor (Trigger op GPIO 17, Echo op GPIO 27)
ultrasonic = DistanceSensor(echo=21, trigger=20, max_distance=2)
ultrasonic2 = DistanceSensor(echo=19, trigger=26, max_distance=2)

try:
    while True:
        
        distance = ultrasonic.distance * 100  # Converteer naar cm
        print(f"Afstand1: {distance:.2f} cm")
        sleep(0.5)
        distance2 = ultrasonic2.distance * 100  # Converteer naar cm
        print(f"Afstand2: {distance2:.2f} cm")
        sleep(0.5)


except KeyboardInterrupt:
    print("\nProgramma gestopt!")