import pyttsx3
import threading

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  
    engine.setProperty('rate', 150)  
    engine.say(text)
    engine.runAndWait()

def start_speaking(text):
    thread = threading.Thread(target=speak, args=(text,))
    thread.start()
