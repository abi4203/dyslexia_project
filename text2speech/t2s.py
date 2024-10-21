from flask import Flask, render_template, request, redirect, url_for,Blueprint
from gtts import gTTS
import os

module5_blueprint = Blueprint('module5', __name__, template_folder='templates')

@module5_blueprint.route('/')
def index():
    return render_template('index.html')

@module5_blueprint.route('/convert', methods=['POST'])
def convert():
    if request.method == 'POST':
        text = request.form['text']
        language = request.form['language']

        # Check if the static folder exists
        if not os.path.exists("static"):
            os.makedirs("static")

        # Remove any previous audio file
        audio_file = "static/speech.mp3"
        if os.path.exists(audio_file):
            os.remove(audio_file)

        # Convert text to speech using gTTS
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(audio_file)

        # Redirect back to the homepage after processing
        return redirect(url_for('module5.index'))

