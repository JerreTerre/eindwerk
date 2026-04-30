#!/usr/bin/env python3
from gpiozero import Button
from adafruit_servokit import ServoKit
from rpi_hardware_pwm import HardwarePWM
from signal import pause
from time import sleep
import sys


# Pin definitions (BCM)
SENSOR_PIN = 17
SWITCH_PIN = 5
PWM_CHANNEL = 2 # PWM0_chan2 = GPIO18 voor hardware PWM

kit = ServoKit(channels=16)
# Initialize components
sensor = Button(SENSOR_PIN, pull_up=False, bounce_time=0.05)
# Treat the toggle as a momentary button: when pressed -> servo 90°, when released -> 0°
switch = Button(SWITCH_PIN)

# Initialize hardware PWM servo
servo = HardwarePWM(pwm_channel=PWM_CHANNEL, hz=50)  # 50Hz voor servos
servo.start(0)  # Start met 0% duty cycle

# Helper functie om hoek naar duty cycle om te zetten
def angle_to_duty_cycle(angle):
    """Convert een hoek (0-180) naar duty cycle (2.5-12.5)""" 
    return 2.5 + (angle / 180.0) * 10.0

# Helper to set servo angle and print state
def set_servo(angle):
    duty_cycle = angle_to_duty_cycle(angle)
    servo.change_duty_cycle(duty_cycle)
    print(f"Servo angle set to: {angle}°")

# Sensor handlers (only control servo while switch is not being held)
def sensor_detected():
    # If the switch is not pressed, sensor controls the servo
    if not switch.is_pressed:
        set_servo(90)
        print("Hand detected - Servo 90° (sensor)")

def sensor_undetected():
    if not switch.is_pressed:
        set_servo(0)
        print("No hand detected - Servo 0° (sensor)")

# Switch handlers: act like a button => press => 90°, release => 0°
def switch_pressed():
    set_servo(90)
    print("Switch pressed - Servo 90° (switch)")

def switch_released():
    # When switch released, return to sensor-controlled state immediately
    # so call the sensor handler to decide final position
    if sensor.is_pressed:
        set_servo(90)
        print("Switch released - sensor still detects -> Servo 90°")
    else:
        set_servo(0)
        print("Switch released - no sensor -> Servo 0°")

try:
    # Wire up handlers
    sensor.when_pressed = sensor_detected
    sensor.when_released = sensor_undetected
    switch.when_pressed = switch_pressed
    switch.when_released = switch_released


    # Keep the program running to allow event handlers to fire
    while True:
        
        sleep(0.1)

except KeyboardInterrupt:
    print("\nProgram stopped by user")
finally:
    # Cleanup
    sensor.close()
    switch.close()
    servo.stop()  # Stop de PWM
    print("PWM gestopt")
    sys.exit()