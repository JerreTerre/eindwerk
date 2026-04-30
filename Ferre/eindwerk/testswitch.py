from gpiozero import Button
from time import sleep

# Create a button object connected to GPIO17
switch = Button(6 ,pull_up=False)  # Change 17 to your actual GPIO pin number

try:
    while True:
        if switch.is_pressed:
            print("Switch is OFFfff")  # Because of pull-up resistor, pressed = OFF
        else:
            print("Switch is ONnnn")   # When not pressed = ON
        sleep(0.1)  # Small delay to prevent CPU overload

except KeyboardInterrupt:
    print("\nProgram stopped by user")
    
