import os
import requests
import time
from flask import Flask, request, jsonify, send_from_directory, Blueprint, render_template

module2_blueprint = Blueprint('module2', __name__, template_folder='templates')

API_KEY = '2fc5b6ce4a25450cbe68287815311ca8'  # Replace with your AssemblyAI API key

@module2_blueprint.route('/')
def serve_index():
    return render_template('s2t.html')

@module2_blueprint.route('/upload', methods=['POST'])
def upload_audio():
    file = request.files['audio']
    
    # Save the uploaded file temporarily
    audio_file_path = 'uploaded_audio.wav'
    file.save(audio_file_path)

    # Upload the audio file to AssemblyAI
    with open(audio_file_path, 'rb') as audio_file:
        headers = {'authorization': API_KEY}
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=audio_file)

    if response.status_code != 200:
        print("Error uploading audio file:", response.json())
        return jsonify({'error': 'Error uploading audio file.'}), response.status_code

    audio_url = response.json()['upload_url']
    print("Audio uploaded successfully, URL:", audio_url)

    # Use AssemblyAI API to transcribe audio
    headers = {'authorization': API_KEY}
    json_data = {'audio_url': audio_url}

    response = requests.post('https://api.assemblyai.com/v2/transcript', headers=headers, json=json_data)

    if response.status_code != 200:
        print("Error requesting transcription:", response.json())
        return jsonify({'error': 'Error requesting transcription.'}), response.status_code

    transcript_id = response.json()['id']
    print("Transcription ID:", transcript_id)

    # Check the status of the transcription
    while True:
        transcript_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        status = transcript_response.json()['status']
        print("Transcription status:", status)
        
        if status == 'completed':
            transcription = transcript_response.json().get('text', '')
            print("Transcription result:", transcription)
            return jsonify({'transcription': transcription})  # Return transcription to frontend
        elif status == 'failed':
            error_message = transcript_response.json().get('error', 'Unknown error occurred.')
            print("Transcription failed:", error_message)
            return jsonify({'error': error_message}), 500
        
        time.sleep(2)  # Wait for a bit before checking again
