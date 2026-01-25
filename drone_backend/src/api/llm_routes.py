from flask import Blueprint, jsonify, request
from src.utils.llm_helper import (
    process_audio_request, 
    process_text_request, 
    reset_parameters,
    get_current_thresholds,
    current_llm_data,
    tuner_lock
)

llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/api/llm', methods=['POST'])
def process_request():
    """Process LLM request (audio or text)"""
    print("\n=== LLM REQUEST RECEIVED ===")
    
    # Handle audio transcription
    if 'audio' in request.files:
        print("Processing audio file...")
        audio_file = request.files['audio']
        print(f"Audio file: {audio_file.filename}, size: {audio_file.content_length}")
        
        result = process_audio_request(audio_file)
        print(f"Result from process_audio_request: {result}")
        return jsonify(result)
    
    # Handle text input
    elif request.json and 'text' in request.json:
        print("Processing text input...")
        text = request.json['text']
        print(f"Text: {text}")
        
        result = process_text_request(text)
        print(f"Result from process_text_request: {result}")
        return jsonify(result)
    
    print("ERROR: No audio or text provided")
    return jsonify({
        'error': 'No audio file or text provided',
        'success': False
    }), 400

@llm_bp.route('/api/llm/thresholds', methods=['GET'])
def get_thresholds():
    """Get current threshold values"""
    thresholds = get_current_thresholds()
    
    if thresholds is None:
        return jsonify({
            'error': 'Parameter tuner not initialized. Start tracking first.'
        }), 400
    
    return jsonify(thresholds)

@llm_bp.route('/api/llm/reset', methods=['POST'])
def reset_thresholds():
    """Reset thresholds to defaults"""
    result = reset_parameters()
    return jsonify(result)

@llm_bp.route('/api/llm/status', methods=['GET'])
def get_status():
    """Get LLM tuning status"""
    global current_llm_data, tuner_lock
    
    with tuner_lock:
        data_copy = current_llm_data.copy()
    
    return jsonify(data_copy)