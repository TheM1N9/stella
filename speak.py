import pyttsx3

# Initialize speech recognition and text-to-speech engines
def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Change index to choose different voices
    engine.say(text)
    engine.runAndWait()