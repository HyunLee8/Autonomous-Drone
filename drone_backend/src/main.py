from flask import Flask, jsonify, request
from flask_cors import CORS                 #import for localHost3000 and localHost5000 communication


app = Flask(__name__)
CORS(app)

@app.route('/llm', methods=['POST'])
def llm_endpoint():