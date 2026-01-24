from flask import Blueprint, jsonify, request, Response
from src.utils import 
import threading

tello_bp = Blueprint('tello', __name__)
intialize_takeoff = False

@tello_bp.route('/api/takeoff', methods=['POST'])
def takeoff():
    global initialize_takeoff

    if not initialize_takeoff: