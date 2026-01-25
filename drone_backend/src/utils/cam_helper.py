from src.tello import get_head_detector
import threading
import cv2

latest_frame = None
head_model = None
frame_lock = threading.Lock()
stop_flag = threading.Event() 

current_drone_data = {
    'forward': False,
    'backward': False,
    'left': False,
    'right': False,
    'up': False,
    'down': False,
    'center': False
}

def run_detection():
    """Run head detection in background thread"""
    global latest_frame, frame_lock, current_drone_data, stop_flag, head_model
    head_model = get_head_detector()
    print(f"DEBUG cam_helper: Using head_detector id: {id(head_model)}")
    print(f"DEBUG: Initial velocities - fb:{head_model.fb_velocity}, ud:{head_model.ud_velocity}, yaw:{head_model.yaw_velocity}")
    def combined_callback(frame, control_values):
        if stop_flag.is_set():
            return
        update_frame (frame)

        with frame_lock:
            current_drone_data.update({
                'forward': head_model.forward,
                'backward': head_model.backward,
                'left': head_model.left,
                'right': head_model.right,
                'up': head_model.up,
                'down': head_model.down,
                'center': head_model.center,
                'face_detected': control_values['face_detected']    
            })
            
    head_model.run_head_detection(frame_callback=combined_callback, stop_flag=stop_flag)

#def run_flight_logic():
#    global 

def generate_frames():
    """Generator function that yields video frames"""
    global latest_frame, frame_lock
    
    while True:
        if stop_flag and stop_flag.is_set():
            break
        with frame_lock:
            if latest_frame is None:
                print("Waiting for first frame...")
                import time
                time.sleep(0.1)
                continue
            frame = latest_frame.copy()
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def update_frame(frame):
    """Update the shared frame for streaming"""
    global latest_frame, frame_lock
    with frame_lock:
        latest_frame = frame