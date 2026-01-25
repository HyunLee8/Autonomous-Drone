from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from src.api import cam_bp, llm_bp, tello_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(cam_bp)
app.register_blueprint(llm_bp)
app.register_blueprint(tello_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)