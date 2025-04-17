import time
import cv2
from ultralytics import YOLO
import threading
import math
import bridge

model = YOLO("red.pt")  
cap = cv2.VideoCapture(1)
CONFIDENCE_THRESHOLD = 0.7
L1 = 10  
L2 = 10  
s = bridge.Element
s.start()

FRAME_WIDTH = int(cap.get(3))  # Get frame width
FRAME_CENTER_X = FRAME_WIDTH // 2  # Find center X

def move_the_arm(x, y, z=100):
    global s
    try:
        theta1, theta2, theta3 = inverse_kinematics(x, y)
        s.send("14", int(theta1))
        time.sleep(0.3)
        s.send("15", int(theta2))
        time.sleep(0.3)
        s.send("18", int(theta3))
        time.sleep(0.3)


        print(f"Moving arm to Theta1: {theta1}, Theta2: {theta2}, Z: {z}")
    except Exception as e:
        print(f"Error in moving arm: {e}")

def inverse_kinematics(x, y):
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

def track_object():
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

                offset_x = FRAME_CENTER_X - x_center  
                x_center_corrected = x_center + offset_x * 0.5  

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  
                detected = True
                print(f"Tracking object at X: {x_center_corrected}, Y: {y_center}, Z: {z}")

                threading.Thread(target=move_the_arm, args=(x_center_corrected, y_center, z)).start()
                break  
            
            if detected:
                break

        cv2.imshow("YOLOv8 Live Object Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

track_object()
