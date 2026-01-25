from src.tello import TelloController
from src.cv import HeadDetector
from src import utils
import time
from src.utils.llm_helper import initialize_tuner
import logging
import threading

logger = logging.getLogger(__name__)
drone = None
head_detector = None
_init_lock = threading.Lock()
_initialized = False

def ensure_initialized():
    global drone, head_detector, _initialized
    
    print(f"DEBUG ensure_initialized: Called, _initialized={_initialized}")
    
    with _init_lock:
        if not _initialized:
            print("Initializing drone and detector...")
            drone = TelloController()
            head_detector = HeadDetector(drone=drone)
            
            print("🔧 Initializing LLM tuner...")
            print(f"DEBUG: head_detector object: {head_detector}")
            print(f"DEBUG: Created head_detector id: {id(head_detector)}")
            initialize_tuner(head_detector)
            print("✅ LLM tuner initialization complete")
            
            _initialized = True
    
    print(f"DEBUG ensure_initialized: Returning, _initialized={_initialized}")
    return drone, head_detector

def get_drone():
    ensure_initialized()
    return drone

def get_head_detector():
    ensure_initialized()
    return head_detector

class FlightLogic:
    def __init__(self):
        ensure_initialized()
        self.drone = get_drone()
        self.head_detector = get_head_detector()
        self.running = True

        #phases
        self.phase = "IDLE"
        self.calibration_complete = False
        self.face_found = False

        #Target settings
        self.target_face_size = 0.1
        self.aruco_marker_id = 0

    def start_flight_sequence(self):
        try:
            #Phase 1
            self.phase = "TAKEOFF"
            if not self._connect_and_takeoff():
                return False

            # Phase 2 - Implement later if Needed
            #self.phase = "CALIBRATING"
            #if not self._calibrate_with_aruco():
            #    self.drone.land()
            #    return False

            #Phase 3
            #self.phase = "SEARCHING"
            #if not self._search_for_face():
            #    self.drone.land()
            #    return False  

            #Phase 4
            self.phase = "TRACKING"
            self._track_face()

            return True

        except Exception as e:
            logger.error(f"Flight sequence error: {e}")
            self.drone.emergency_land()
            return False

    def _connect_and_takeoff(self):
        logger.info("Connecting to drone... ")
        if not self.drone.connect():
            logger.error("Failed to connect to drone.")
            return False
        
        logger.info("starting video stream...")
        if not self.drone.stream_on():
            logger.error("Failed to start video stream.")
            return False
        
        if not self.drone.wait_for_stream(timeout=10):
            logger.error("Video stream not ready.")
            return False

        logger.info("Taking off...")
        if not self.drone.takeoff():
            logger.error("Failed to take off.")
            return False

        logger.info("Takeoff successful.")
        return True

    def _search_for_face(self, timeout=60):
        logger.info("Searching for face...")
        start_time = time.time()

        rotation_step = 30
        total_rotation = 0

        while time.time() - start_time < timeout and total_rotation < 360:
            frame = self.drone.get_frame()
            if frame is None:
                continue

            face_detected = self.head_detector.FoundHead(frame)
            if face_detected:
                logger.info("Face found!")
                self.face_found = True
                return True
    
            logger.info(f"No face detected, rotating {rotation_step}°...")
            self.drone.rotate_clockwise(rotation_step)
            total_rotation += rotation_step
            time.sleep(1)
        
        self.drone.emergency_land()
        logger.error("Failed to find face within timeout.")
        return False

    def _track_face(self):
        logger.info("Tracking face...")
        while self.running:
            self.drone.send_rc_control(
                head_detector.lr_velocity,
                head_detector.fb_velocity,
                head_detector.ud_velocity,
                head_detector.yaw_velocity
            )
            
            time.sleep(0.1)
        
        logger.info("Tracking stopped")
    
    def stop(self):
        logger.info("Stopping flight logic and landing drone...")
        self.running = False 
        self.phase = "IDLE"
        time.sleep(0.2)
        self.drone.land()