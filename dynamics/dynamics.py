import RPi.GPIO as GPIO
import threading
import time

GPIO.setmode(GPIO.BCM)

SHOULDER1_PIN = 14
SHOULDER2_PIN = 15
ELBOW_PIN = 18
WRIST_PIN = 23
FINGERS_PIN = 24

GPIO.setup(SHOULDER1_PIN, GPIO.OUT)
GPIO.setup(SHOULDER2_PIN, GPIO.OUT)
GPIO.setup(ELBOW_PIN, GPIO.OUT)
GPIO.setup(WRIST_PIN, GPIO.OUT)
GPIO.setup(FINGERS_PIN, GPIO.OUT)

shoulder1 = GPIO.PWM(SHOULDER1_PIN, 50) 
shoulder2 = GPIO.PWM(SHOULDER2_PIN, 50)  
elbow = GPIO.PWM(ELBOW_PIN, 50)         
wrist = GPIO.PWM(WRIST_PIN, 50)          
fingers = GPIO.PWM(FINGERS_PIN, 50)     


def angle_to_duty_cycle(angle):
    return 2.5 + (angle / 18.0)

def move_servo_to_angle(servo, current_angle, target_angle):
    step = 1 if target_angle > current_angle else -1
    for angle in range(current_angle, target_angle + step, step):
        duty_cycle = angle_to_duty_cycle(angle)
        servo.ChangeDutyCycle(duty_cycle)
        time.sleep(0.02)
    servo.ChangeDutyCycle(angle_to_duty_cycle(target_angle))

def control_servos(angles):
    global current_angles

    angles['shoulder2'] = 180 - angles['shoulder1']

    threads = [
        threading.Thread(target=move_servo_to_angle, args=(shoulder1, current_angles['shoulder1'], angles['shoulder1'])),
        threading.Thread(target=move_servo_to_angle, args=(shoulder2, current_angles['shoulder2'], angles['shoulder2'])),
        threading.Thread(target=move_servo_to_angle, args=(elbow, current_angles['elbow'], angles['elbow'])),
        threading.Thread(target=move_servo_to_angle, args=(wrist, current_angles['wrist'], angles['wrist'])),
        threading.Thread(target=move_servo_to_angle, args=(fingers, current_angles['fingers'], angles['fingers']))
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    current_angles.update(angles)

def cleanup():
    shoulder1.stop()
    shoulder2.stop()
    elbow.stop()
    wrist.stop()
    fingers.stop()
    GPIO.cleanup()