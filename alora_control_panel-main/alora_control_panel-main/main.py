import cv2
import numpy as np
import torch
from flask import Flask, render_template, Response, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'sdhgsydfg'

camera = cv2.VideoCapture(0)

model = torch.hub.load('ultralytics/yolov5', 'yolov5m')  

def detect_objects(frame):
    results = model(frame)  
    results = results.xyxy[0].numpy()  

    for *box, conf, cls in results:
        x1, y1, x2, y2 = map(int, box)  
        label = f'{model.names[int(cls)]} {conf:.2f}' 
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) 
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  

    return frame

def generate_frames():
    while True:
        success, frame = camera.read() 
        if not success:
            break
        else:
            frame = detect_objects(frame)  
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
    app.run(debug=True, host="0.0.0.0")
