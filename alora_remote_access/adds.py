speak.start_speaking("Welcome to ALORA")
time.sleep(4)
speak.start_speaking("Booting Systems")
time.sleep(4)
starter=bridge.start()

speak.start_speaking(starter)

model = YOLO("red.pt")  

detected=False
cap = cv2.VideoCapture(1)

CONFIDENCE_THRESHOLD = 0.7  
CONFIRMATION_TIME = 1

detected_start_time = None  
time.sleep(4)
speak.start_speaking("attempting a scan for the  blue basket in the surrounding")

bridge.send(18,0)
bridge.send(14,0)
bridge.send(15,115)
