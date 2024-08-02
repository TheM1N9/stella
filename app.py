from flask import Flask, render_template, request, jsonify
import json
import os
from features.speak import speak
from web_assistant import personal_assistant, conversation_history
import threading

app = Flask(__name__)
IMAGE_FOLDER = os.path.join('static', 'images')

@app.route('/')
def index():
    stella_image = os.path.join(IMAGE_FOLDER, 'stella.png')
    return render_template('index.html', profile_pic=stella_image)

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')  # type: ignore
    response = personal_assistant(user_message)

    # Create a new thread to call the speak function
    # threading.Thread(target=speak, args=(response,)).start()

    return jsonify({'user_message': user_message, 'response': response})

@app.route('/conversation_history', methods=['GET'])
def get_conversation_history():
    return jsonify(conversation_history)

if __name__ == '__main__':
    app.run(debug=True)
