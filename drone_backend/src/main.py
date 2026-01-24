from flask import Flask, jsonify, request
from flask_cors import CORS                 #import for localHost3000 and localHost5000 communication
from src.llm import get_agent_response, transcribe_audio

app = Flask(__name__)
CORS(app)

@app.route('/api/process', methods=['POST'])
def process_request():
    if 'audio' in request.files:
        audio_file = request.files['audio']
        transcription = transcribe_audio(audio_file)
    if not transcription:
        return jsonify({'message': 'I didn\'t catch that. Could you please repeat?'})
    message = get_agent_response(transcription)
    return jsonify({'transcription': transcription, 'message': message})