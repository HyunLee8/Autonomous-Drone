from src.tello import TelloController
from src import utils
import time
import logging

logger = logging.getLogger(__name__)

class FlightLogic:
    
    def __init__(self):
        self.drone = TelloController()
        self.aruco_detector = ArucoDetector()
        self.head_detector = HeadDetector(drone_controller=self.drone)

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
            self.phase = "SEARCHING"
            if not self._search_for_face():
                self.drone.land()
                return False  

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

        time.sleep(1)

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

        def frame_callback(frame, control_values):
            """Receive frame and control values, send commands to drone"""
            # You can add custom logic here before sending commands
            if control_values['face_detected']:
                # Send the commands to drone
                self.drone.send_rc_control(
                    head_model.lr_velocity,
                    head_model.fb_velocity,
                    head_model.ud_velocity,
                    head_model.yaw_velocity
                )
            else:
                # No face detected - hover in place
                self.drone.send_rc_control(0, 0, 0, 0)

        # Run detection WITHOUT sending commands directly
        self.head_detector.run_head_detection(
            frame_callback=frame_callback,
            send_commands=False  # FlightLogic controls when to send
        )

    def stop(self):
        logger.info("Stopping flight logic and landing drone...")
        self.phase = "IDLE"
        self.drone.land()