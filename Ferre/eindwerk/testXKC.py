from gpiozero import Button
from signal import pause

SENSOR_PIN = 10  # BCM pin

sensor = Button(SENSOR_PIN, pull_up=False)

def on_high():
    print("hoog")

def on_low():
    print("laag")

sensor.when_pressed = on_high
sensor.when_released = on_low

# Print initial state once
if sensor.is_pressed:
    print("hoog")
else:
    print("laag")

try:
    pause()
except KeyboardInterrupt:
    sensor.close()
