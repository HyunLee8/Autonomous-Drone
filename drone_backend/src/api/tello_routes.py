from src.utils import run_logic, stop_logic
from flask import Blueprint, jsonify, request, Response

tello_bp = Blueprint('tello', __name__)
initialize_takeoff = False

@tello_bp.route('/api/takeoff', methods=['POST'])
def takeoff():
    global initialize_takeoff

    if not initialize_takeoff:
        initialize_takeoff = True
        run_logic()
        return jsonify({'message': 'Drone takeoff initiated'})
    return jsonify({'message': 'Drone is already in flight'})

@tello_bp.route('/api/land', methods=['POST'])
def land():
    global initialize_takeoff

    if initialize_takeoff:
        stop_logic()
        initialize_takeoff = False
        return jsonify({'message': 'Drone landing initiated'})
    return jsonify({'message': 'Drone is already landed'})