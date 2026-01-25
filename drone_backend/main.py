from flask import Flask
from flask_cors import CORS
from src.api.cam_routes import cam_bp
from src.api.tello_routes import tello_bp
from src.api.llm_routes import llm_bp
import threading

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(cam_bp)
app.register_blueprint(tello_bp)
app.register_blueprint(llm_bp)

def background_init():
    """Initialize systems in background without blocking"""
    import time
    time.sleep(0.5)  # Small delay to let Flask finish starting
    print("Background initialization starting...")
    from src.tello.flight_logic import ensure_initialized
    ensure_initialized()
    print("Background initialization complete")

init_thread = threading.Thread(target=background_init, daemon=True)
init_thread.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)