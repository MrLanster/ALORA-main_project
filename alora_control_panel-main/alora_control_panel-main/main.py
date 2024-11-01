import cv2
from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
import RPi.GPIO as GPIO
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

GPIO.setmode(GPIO.BCM)
servo_pins = {
    2: 2,
    3: 3,
    4: 4,
    17: 17
}

for pin in servo_pins.values():
    GPIO.setup(pin, GPIO.OUT)

current_angles = {pin: 90 for pin in servo_pins.values()}  

camera = cv2.VideoCapture(0)

def angle_to_duty_cycle(angle):

    return 2.5 + (angle / 18)

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

@app.route('/move/<int:gpio_num>/<direction>')
def move(gpio_num, direction):
    if gpio_num in servo_pins:
        pin = servo_pins[gpio_num]
        pwm = GPIO.PWM(pin, 50)  
        pwm.start(0)  

        if direction == 'left':
            if current_angles[pin] + 20 <= 180:  
                current_angles[pin] += 20
        elif direction == 'right':
            if current_angles[pin] - 20 >= 0:  
                current_angles[pin] -= 20
        else:
            return 'Invalid direction', 400  

        duty_cycle = angle_to_duty_cycle(current_angles[pin])
        pwm.ChangeDutyCycle(duty_cycle)  
        time.sleep(0.5)  
        pwm.ChangeDutyCycle(0)  
        pwm.stop()  

        return f'Servo {gpio_num} moved {direction} to {current_angles[pin]} degrees', 200  
    else:
        return 'Invalid GPIO pin', 404  

if __name__ == '__main__':
    try:
        app.run(debug=True, host="0.0.0.0")
    finally:
        GPIO.cleanup()