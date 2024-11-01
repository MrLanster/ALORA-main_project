import cv2
from flask import Flask, render_template, Response, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for session management

# Initialize the webcam
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()  # Read the frame from the camera
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()  # Convert the frame to bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Send frame as response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        # Check if the credentials are correct
        if username == 'aloraadmin' and password == 'alorapassword':
            session['username'] = username  # Add session
            return redirect(url_for('main'))  # Redirect to main page
        else:
            flash('Invalid username or password')  # Show error message
            return redirect(url_for('index'))  # Redirect back to login

    return render_template('login.html')
@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/main')
def main():
    if 'username' in session:
        return render_template('main.html', username=session['username'])
    return redirect(url_for('index'))  # Redirect to login if not authenticated

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the session
    return redirect(url_for('index'))  # Redirect to login page

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
