import math


L1 = 10 
L2 = 10  

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

    return base_angle-40, 180+10-shoulder_angle, elbow_angle+20

print(calculate_servo_angles( 466, 54))
