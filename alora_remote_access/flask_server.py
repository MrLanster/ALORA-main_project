import cv2
import numpy as np
import torch
from flask import Flask, render_template, Response, request, redirect, url_for, session, flash,jsonify
from flask_socketio import SocketIO, emit
import threading
import bridge
import speak
import time
import math

app = Flask(__name__)
app.secret_key = 'sdhgsydfg'

socketio = SocketIO(app, cors_allowed_origins="*")  

camera = cv2.VideoCapture(1)
lock = threading.Lock()  
BASE_ANGLE=90
SHOULDER_ANGLE=90
ELBOW_ANGLE=90
FINGERS_ANGLE=90



BASE={"14":BASE_ANGLE}
SHOULDER={"15":SHOULDER_ANGLE}
ELBOW={"18":ELBOW_ANGLE}
FINGERS={"23":FINGERS_ANGLE}


L1 = 10 
L2 = 10  

def calculate_servo_angles(x, y, z):
    try:
        base_angle = math.degrees(math.atan2(y, x))

        D = math.sqrt(x**2 + y**2)
        D = min(max(D, abs(L1 - L2)), L1 + L2) 

        cos_theta2 = (D**2 - L1**2 - L2**2) / (2 * L1 * L2)
        cos_theta2 = max(min(cos_theta2, 1), -1)  
        elbow_angle = math.degrees(math.acos(cos_theta2))

        theta1 = math.degrees(math.atan2(y, x))
        cos_alpha = (L1**2 + D**2 - L2**2) / (2 * L1 * D)
        cos_alpha = max(min(cos_alpha, 1), -1)  
        alpha = math.degrees(math.acos(cos_alpha))

        shoulder_angle = (theta1 - alpha)
        elbow_angle = 180 - elbow_angle

        shoulder_angle = 90 - shoulder_angle
        elbow_angle = 180 - elbow_angle

        base_angle = max(0, min(180, base_angle + 90))
        shoulder_angle = max(0, min(180, shoulder_angle))
        elbow_angle = max(0, min(180, elbow_angle))

        wrist_angle = max(0, min(180, 90 - math.degrees(math.atan2(z, D))))

        return base_angle - 40, 180 + 10 - shoulder_angle, elbow_angle + 20, wrist_angle

    except Exception as e:
        print("Error in calculate_servo_angles:", str(e))
        return 90, 90, 90, 90  
    
def mover(pin,angle):
    if angle>180:
        angle=180
    if angle<0:
        angle=0
    s.send(pin,str(angle))

def async_calculate_and_move(x, y, z):
    cx, cy, cz, cw = calculate_servo_angles(x, y, z)
    cx=int(cx)
    cy=int(cy)
    cz=int(cz)
    cw=int(cw)

    threading.Thread(target=mover, args=("14", cx)).start()
    time.sleep(0.3)
    threading.Thread(target=mover, args=("15", cy)).start()
    time.sleep(0.3)
    threading.Thread(target=mover, args=("18", cz)).start()
    time.sleep(0.3)
    threading.Thread(target=mover, args=("23", cw)).start()

@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    try:
        data = request.get_json()
        x = int(data.get("x", 0))
        y = int(data.get("y", 0))
        z = int(data.get("z", 0))

        threading.Thread(target=async_calculate_and_move, args=(x, y, z)).start()

        return jsonify({"status": "success", "message": "Coordinates update started"}), 202

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/get_range")
def get_range():
    temp=s.send("1","1")
    return jsonify({"range": temp}) 

@app.route("/get_temp")
def get_temp():
    temp=s.send("2","2")
    return jsonify({"cpu_temp": temp}) 

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('server_response', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('client_message')
def handle_client_message(data):
    global BASE_ANGLE,BASE
    global SHOULDER_ANGLE,SHOULDER
    global ELBOW_ANGLE,ELBOW
    global FINGERS_ANGLE,FINGERS
    print(f"Received from client: {data}")
    if data["data"]["axis"]=="base":
        pin="14"
        if data["data"]["path"]=="left":
            BASE_ANGLE-=5
        if data["data"]["path"]=="right":
            BASE_ANGLE+=5
        BASE[pin]=BASE_ANGLE
        threading.Thread(target=mover,args=(pin,BASE_ANGLE)).start()


    if data["data"]["axis"]=="shoulder":
        pin="15"
        if data["data"]["path"]=="left":
            SHOULDER_ANGLE-=5
        if data["data"]["path"]=="right":
            SHOULDER_ANGLE+=5
        SHOULDER[pin]=SHOULDER_ANGLE
        threading.Thread(target=mover,args=(pin,SHOULDER_ANGLE)).start()
    if data["data"]["axis"]=="elbow":
        pin="18"
        if data["data"]["path"]=="left":
            ELBOW_ANGLE-=5
        if data["data"]["path"]=="right":
            ELBOW_ANGLE+=5
        ELBOW[pin]=ELBOW_ANGLE
        threading.Thread(target=mover,args=(pin,ELBOW_ANGLE)).start()
    if data["data"]["axis"]=="fingers":
        pin="23"
        if data["data"]["path"]=="left":
            FINGERS_ANGLE-=5
        if data["data"]["path"]=="right":
            FINGERS_ANGLE+=5
        FINGERS[pin]=FINGERS_ANGLE
        threading.Thread(target=mover,args=(pin,FINGERS_ANGLE)).start()
    value=data["data"]["axis"]
    emit('server_response', {'message': f"Server :Moved {value} into position!"}, broadcast=True)


def generate_frames():
    while True:
        success, frame = camera.read() 
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()  
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        if username == 'aloraadmin' and password == 'alorapassword':
            session['username'] = username  
            return redirect(url_for('main'))  
        else:
            flash('Invalid username or password') 
            return redirect(url_for('index'))  

    return render_template('login.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/main')
def main():
    if 'username' in session:
        return render_template('main.html', username=session['username'])
    return redirect(url_for('index'))  

@app.route('/logout')
def logout():
    session.pop('username', None)  
    return redirect(url_for('index'))  

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    s=bridge.Element
    val=s.start()
    
    speak.speak(val)
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)