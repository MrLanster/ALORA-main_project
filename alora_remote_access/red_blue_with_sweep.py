import time
import cv2
from ultralytics import YOLO
import threading
import math
import bridge

model = YOLO("red.pt")  
cap = cv2.VideoCapture(1)
CONFIDENCE_THRESHOLD = 0.8
L1 = 10 
L2 = 10  
detected=False
s=bridge.Element
s.start()

def calculate_servo_angles(x, y, z):
    base_angle = math.degrees(math.atan2(y, x))
    base_angle_offset = base_angle - 90  
    D = math.sqrt(x**2 + y**2)
    D = min(max(D, abs(L1 - L2)), L1 + L2)  
    cos_theta2 = (D**2 - L1**2 - L2**2) / (2 * L1 * L2)
    elbow_angle = math.degrees(math.acos(cos_theta2))
    theta1 = math.degrees(math.atan2(y, x))
    cos_alpha = (L1**2 + D**2 - L2**2) / (2 * L1 * D)
    alpha = math.degrees(math.acos(cos_alpha))
    shoulder_angle = (theta1 - alpha)  
    elbow_angle = 180 - elbow_angle  
    shoulder_angle = 90 - shoulder_angle  
    elbow_angle = 180 - elbow_angle  
    base_angle = max(0, min(180, base_angle + 90))
    shoulder_angle = max(0, min(180, shoulder_angle))
    elbow_angle = max(0, min(180, elbow_angle))
    z_angle = max(0, min(180, z))
    return base_angle-40+20, 180+50-shoulder_angle+35, elbow_angle+20, z_angle

def mover(x, y, z):
    global s
    global detected
    s.send("24","150")
    time.sleep(0.5)
    s.send("14",str(x))
    time.sleep(0.3)
    s.send("15",str(y))
    time.sleep(0.3)
    s.send("18",str(z))
    time.sleep(2)
    s.send("24","90")
    time.sleep(4)
    time.sleep(1)
    val=s.send("2","0")

    s.send("14","90")
    time.sleep(1)
    s.send("15","90")
    time.sleep(1)
    s.send("18","90")
    time.sleep(1)
    s.send("24","90")
    s.send("14","180")
    time.sleep(1)
    s.send("15","150")
    time.sleep(1)
    s.send("18","30")
    time.sleep(1)
    s.send("24","150")
    time.sleep(2)
    s.send("14","90")
    time.sleep(1)
    s.send("15","90")
    time.sleep(1)
    s.send("18","90")
    time.sleep(1)
    s.send("24","90")
    time.sleep(5)
    detected=False
    detect_red_cube()

def move_the_arm(cx, cy, cz):
    x, y, z, z_angle = calculate_servo_angles(cx, cy, cz)
    x, y, z, z_angle = int(x), int(y), int(z), int(z_angle)
    threading.Thread(target=mover, args=(x, y, z,)).start()
    print("moving arm to pos", x, y, z, "Z-Angle:", z_angle)

def start_sweep():
    global detected
    angle = 90
    s.send("14", str(angle))
    step = 5
    while not detected:
        angle += step
        time.sleep(0.2)
        s.send("14", str(angle))
        if angle > 180:
            step = -5
        if angle < 0:
            step = 5

def detect_red_cube():
    global detected
    threading.Thread(target=start_sweep, args=()).start()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame, conf=CONFIDENCE_THRESHOLD)
        detected = False  
        for r in results:
            for box in r.boxes.xyxy:
                x1, y1, x2, y2 = map(int, box)  
                x_center = (x1 + x2) // 2
                y_center = (y1 + y2) // 2
                z = 100 
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  
                detected = True
                time.sleep(1)
                print(f"Detected at X: {x_center}, Y: {y_center}, Z: {z}")
                break
            if detected:
                break
        if detected:
            threading.Thread(target=move_the_arm, args=(x_center, y_center, z)).start()
            break

detect_red_cube()