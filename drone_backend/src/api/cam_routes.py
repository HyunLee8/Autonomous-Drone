from flask import Blueprint, jsonify, request, Response
from src.utils import run_detection, generate_frames, current_drone_data, frame_lock, stop_flag, drone
import threading

cam_bp = Blueprint('cam', __name__)
tracking_started = False

@cam_bp.route('/api/start-tracking', methods=['POST'])
def start_tracking():
    """Start tracking endpoint"""
    global tracking_started

    if not tracking_started:
        stop_flag.clear()  # Ensure stop flag is cleared
        tracking_started = True
        thread = threading.Thread(target=run_detection, daemon=True)
        thread.start()

    return jsonify({'message': 'Tracking started'})

@cam_bp.route('/api/video-tracking', methods=['GET'])
def video_feed():
    """Video streaming route - starts tracking and returns stream"""
    global tracking_started

    print(f"Active threads: {threading.active_count()}")  # Debug
    print(f"Tracking started: {tracking_started}") 

    # Start tracking in background if not already started
    if not tracking_started:
        stop_flag.clear()  # Ensure stop flag is cleared
        tracking_started = True
        thread = threading.Thread(target=run_detection, daemon=True)
        thread.start()

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@cam_bp.route('/api/stop-tracking', methods=['POST'])
def stop_tracking():
    """Stop tracking endpoint"""
    global tracking_started

    if tracking_started:
        stop_flag.set()  # Signal threads to stop
        tracking_started = False
        return jsonify({'message': 'Tracking stopped'})

    return jsonify({'message': 'Tracking was not running'})

@cam_bp.route('/api/logged-data', methods=['GET'])
def get_logged_data():
    global current_drone_data, frame_lock
    with frame_lock:
        # Create a copy to avoid race conditions
        data_copy = current_drone_data.copy()