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


s=bridge.Element
s.start()

def calculate_servo_angles(x, y):
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

    return base_angle-40+20, 180+10-shoulder_angle+25, elbow_angle+20

def mover(x,y,z):
    global s
    s.send("24","150")
    time.sleep(0.5)
    s.send("14",str(x))
    time.sleep(0.3)
    s.send("15",str(y))
    time.sleep(0.3)
    s.send("18",str(z))
    time.sleep(2)
    s.send("24",str("90"))

    time.sleep(4)
    time.sleep(1)
    s.send("14","90")
    time.sleep(1)
    s.send("15","90")
    time.sleep(1)
    s.send("18","90")
    time.sleep(1)
    s.send("24","90")
    time.sleep(3)
    s.send("14","180")
    time.sleep(1)
    s.send("15","150")
    time.sleep(1)
    s.send("18","50")
    time.sleep(1)
    s.send("24","150")
    time.sleep(3)

    time.sleep(1)
    s.send("14","90")
    time.sleep(1)
    s.send("15","90")
    time.sleep(1)
    s.send("18","90")
    time.sleep(1)
    s.send("24","90")

#pos of the blue basket is 14:180,15:150,18:30

def move_the_arm(cx,cy):
    x,y,z=calculate_servo_angles(cx,cy)
    x=int(x)
    y=int(y)
    z=int(z)
    threading.Thread(target=mover,args=(x,y,z,)).start()
    print("moving arm to pos",x,y,z)



def detect_red_cube():
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
                print(f"Detected at X: {x_center}, Y: {y_center}, Z: {z}")
                break
            if detected:
                break
        if detected:
            threading.Thread(target=move_the_arm,args=(x_center,y_center)).start()
            break
    

        cv2.imshow("YOLOv8 Live Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

detect_red_cube()