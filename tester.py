import RPi.GPIO as GPIO
import time

# Set up the GPIO pin and PWM
servo_pin = 2
GPIO.setmode(GPIO.BCM)         # Use BCM GPIO numbering
GPIO.setup(servo_pin, GPIO.OUT) # Set GPIO pin as output

# Set up PWM with a 50Hz frequency (most servos work well with 50Hz)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)  # Start with 0 duty cycle (servo at 0 degrees)

# Function to set servo angle
def set_angle(angle):
    duty = 2 + (angle / 18)  # Convert angle to duty cycle for 0-180 degrees
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Delay to allow servo to move to position
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)  # Stop sending signals to prevent jitter

try:
    while True:
        # Move from 0 to 180 degrees
        set_angle(0)
        time.sleep(1)
        set_angle(180)
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping script...")

finally:
    # Clean up GPIO settings
    pwm.stop()
    GPIO.cleanup()
