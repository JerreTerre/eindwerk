from rpi_hardware_pwm import HardwarePWM
from time import sleep
DC=7.5 # duty cycle for 90 degree
while True:
    pwm = HardwarePWM(pwm_channel=0, hz=50, chip=0)
    pwm.start(5) # full duty cycle
    pwm.change_duty_cycle(DC)
    sleep(1)