#!/usr/bin/python3
from rpi_hardware_pwm import HardwarePWM
import time

# Hardware PWM op GPIO18 (PWM0_chan2)
# We gebruiken PWM0 kanaal 2 op GPIO18
pwm_channel = 2  # PWM0_chan2 = GPIO18
 
def setup_servo():
    """Initialize de hardware PWM voor servo control"""
    pwm = HardwarePWM(pwm_channel=pwm_channel, hz=50)  # 50Hz voor servos
    pwm.start(0)  # Start met 0% duty cycle
    return pwm

def angle_to_duty_cycle(angle):
    """Convert een hoek (0-180) naar duty cycle (2.5-12.5)"""
    # Meeste servo's gebruiken:
    # 2.5% duty cycle = 0 graden
    # 7.5% duty cycle = 90 graden  
    # 12.5% duty cycle = 180 graden
    return 2.5 + (angle / 180.0) * 10.0

def main():
    try:
        # Setup PWM
        servo = setup_servo()
        print("Servo geïnitialiseerd op PWM kanaal", pwm_channel)
        
        while True:
            # Draai naar 0 graden
            print("Draai naar 0 graden")
            servo.change_duty_cycle(angle_to_duty_cycle(0))
            time.sleep(1)
            
            # Draai naar 90 graden
            print("Draai naar 90 graden")
            servo.change_duty_cycle(angle_to_duty_cycle(90))
            time.sleep(1)
            
            # Wacht 2 seconden voor we opnieuw beginnen
            print("Wacht 2 seconden...")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nProgramma gestopt door gebruiker")
    finally:
        # Cleanup
        servo.stop()
        print("PWM gestopt")

if __name__ == '__main__':
    main()