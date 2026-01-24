import cv2
import numpy as np
from ultralytics import YOLO
import os
import time

class HeadDetector:
    def __init__(self, model_path=None, drone=None):
        """
        Initialize YOLO-based head detector using pose estimation
        model_path: Path to YOLO pose model (e.g., 'yolov8n-pose.pt')
                   If None, will download YOLOv8n-pose automatically
        """
        if model_path is None:
            model_path = os.path.expanduser('~/.ultralytics/weights/yolov8n-pose.pt')
        self.drone = drone
        self.model_path = model_path
        self.frame_count = 0
        self._initialize_yolo()
        self.tello_controller = drone
        
        # Direction flags
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.forward = False
        self.backward = False
        self.center = False
        
        # Velocity attributes
        self.lr_velocity = 0
        self.fb_velocity = 0
        self.ud_velocity = 0
        self.yaw_velocity = 0

    def _initialize_yolo(self):
        """Initialize YOLO pose model for head detection"""
        print(f"Loading YOLO pose model: {self.model_path}")
        self.model = YOLO(self.model_path)
        print("YOLO pose model loaded successfully")

    def drone_directions(self, x, y, frame_width, frame_height, face_size, forward_threshold=100, backward_threshold=200):
        """Determine drone movement directions based on head position with circular deadzone"""
        # Calculate distance from center
        center_x = frame_width // 2
        center_y = frame_height // 2
        distance_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Circular deadzone - roughly the size of the center square (1/3 of frame width)
        deadzone_radius = frame_width // 3
        
        # If within circular deadzone, stay centered
        if distance_from_center < deadzone_radius:
            # Only handle forward/backward movement when centered
            if face_size < forward_threshold:
                self.center, self.forward = True, True
                self.left, self.right, self.up, self.down, self.backward = False, False, False, False, False
            elif face_size > backward_threshold:
                self.center, self.backward = True, True
                self.left, self.right, self.up, self.down, self.forward = False, False, False, False, False
            else:
                self.center = True
                self.left, self.right, self.up, self.down, self.backward, self.forward = False, False, False, False, False, False
            return
        
        # Outside deadzone - determine direction based on position
        # Calculate angle from center (0° = right, 90° = up, 180° = left, 270° = down)
        angle = np.degrees(np.arctan2(center_y - y, x - center_x))
        if angle < 0:
            angle += 360
        
        # Reset all directions
        self.left = self.right = self.up = self.down = False
        self.forward = self.backward = self.center = False
        
        # Set directional flags based on angle
        if 337.5 <= angle or angle < 22.5:  # Right
            self.right = True
        elif 22.5 <= angle < 67.5:  # Up-Right
            self.up = self.right = True
        elif 67.5 <= angle < 112.5:  # Up
            self.up = True
        elif 112.5 <= angle < 157.5:  # Up-Left
            self.up = self.left = True
        elif 157.5 <= angle < 202.5:  # Left
            self.left = True
        elif 202.5 <= angle < 247.5:  # Down-Left
            self.down = self.left = True
        elif 247.5 <= angle < 292.5:  # Down
            self.down = True
        else:  # 292.5 <= angle < 337.5: Down-Right
            self.down = self.right = True
        
        # Add forward/backward based on face size
        if face_size < forward_threshold:
            self.forward = True
        elif face_size > backward_threshold:
            self.backward = True

    def FoundHead(self, frame):
        """Quick check if a head is detected in the frame"""
        try:
            results = self.model(frame, verbose=False, conf=0.3)
            
            # Check if any person with keypoints is detected
            if results[0].keypoints is not None and len(results[0].keypoints) > 0:
                return True
            return False
        except Exception as e:
            print(f'Error in FoundHead: {e}')
            return False

    def run_head_detection(self, frame_callback=None, stop_flag=None, send_commands=False):
        """Main detection loop"""
        print("Initializing YOLO pose detection...")
        drone = self.drone

        cap = None

        # Use Tello camera if drone exists, otherwise webcam
        if drone is not None:
            print("Using Tello camera...")
            print("Waiting for drone video stream...")
            
            # Wait for first valid frame
            timeout = 10
            start_time = time.time()
            first_frame = None
            
            while first_frame is None and time.time() - start_time < timeout:
                first_frame = drone.get_frame()
                if first_frame is None:
                    time.sleep(0.1)
            
            if first_frame is None:
                print("Error: Could not get video stream from drone")
                return
            
            print("Drone video stream ready!")
            
            def get_frame():
                return drone.get_frame()
        else:
            print("Opening webcam...")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print('Error: Could not open camera.')
                return
            def get_frame():
                ret, frame = cap.read()
                return frame if ret else None

        print("Starting detection loop... Press 'q' to quit")

        frame_count = 0
        try:
            while True:
                if stop_flag and stop_flag.is_set():
                    break 
                    
                frame = get_frame()
                if frame is None:
                    print('Error: Could not read frame.')
                    break

                h, w, _ = frame.shape
                x_center = w // 2
                y_center = h // 2
                radius = h // 2

                square_frame = frame[0:h, x_center - radius : x_center + radius]
                new_h, new_w, _ = square_frame.shape

                x1, x2 = int(new_w/3), int(new_w*2/3)
                y1, y2 = int(new_h/3), int(new_h*2/3)
                new_x_center, new_y_center = new_w // 2, new_h // 2

                # Draw grid
                x1, x2, x3, x4 = 0, x1, x2, new_w
                y1, y2, y3, y4 = 0, y1, y2, new_h

                cv2.rectangle(square_frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                cv2.rectangle(square_frame, (x2, y1), (x3, y2), (255, 255, 255), 2)
                cv2.rectangle(square_frame, (x3, y1), (x4, y2), (255, 255, 255), 2)
                cv2.rectangle(square_frame, (x1, y2), (x2, y3), (255, 255, 255), 2)
                cv2.rectangle(square_frame, (x2, y2), (x3, y3), (255, 255, 255), 2)
                cv2.rectangle(square_frame, (x3, y2), (x4, y3), (255, 255, 255), 2)
                cv2.rectangle(square_frame, (x1, y3), (x2, y4), (255, 255, 255), 2)
                cv2.rectangle(square_frame, (x2, y3), (x3, y4), (255, 255, 255), 2)
                cv2.rectangle(square_frame, (x3, y3), (x4, y4), (255, 255, 255), 2)

                # Draw circular deadzone (radius = 1/3 of frame width)
                deadzone_radius = new_w // 3
                cv2.circle(square_frame, (new_x_center, new_y_center), deadzone_radius, (0, 255, 255), 3)
                cv2.circle(square_frame, (new_x_center, new_y_center), 20, (255, 255, 255), -1)
                
                frame_count += 1
                
                # Run YOLO pose detection
                results = self.model(frame, verbose=False, conf=0.3)

                control_values = {
                    'face_detected': False
                }

                # Process pose detections - track HEAD using keypoints
                head_detected = False
                
                if results[0].keypoints is not None and len(results[0].keypoints) > 0:
                    # Get keypoints for first person
                    keypoints = results[0].keypoints.xy[0].cpu().numpy()
                    
                    # YOLO pose keypoints:
                    # 0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear
                    # We'll use nose (0) as head center, and eyes to calculate head size
                    
                    nose = keypoints[0]
                    left_eye = keypoints[1]
                    right_eye = keypoints[2]
                    
                    # Check if nose is detected (confidence > 0)
                    if nose[0] > 0 and nose[1] > 0:
                        head_detected = True
                        control_values['face_detected'] = True
                        
                        x_head_center = int(nose[0])
                        y_head_center = int(nose[1])
                        
                        # Calculate head size based on eye distance
                        if left_eye[0] > 0 and right_eye[0] > 0:
                            eye_distance = np.sqrt((right_eye[0] - left_eye[0])**2 + 
                                                  (right_eye[1] - left_eye[1])**2)
                            # Head width is approximately 2x eye distance
                            head_size = int(eye_distance * 2)
                        else:
                            # Fallback if eyes not detected - use fixed size
                            head_size = 100
                        
                        # Draw square around head
                        half_size = head_size // 2
                        x_min = x_head_center - half_size
                        x_max = x_head_center + half_size
                        y_min = y_head_center - half_size
                        y_max = y_head_center + half_size
                        
                        x_head_in_square = x_head_center - (x_center - radius)
                        y_head_in_square = y_head_center
                        
                        # Draw HEAD bounding box
                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
                        cv2.circle(frame, (x_head_center, y_head_center), 5, (0, 255, 0), -1)
                        cv2.line(frame, (x_head_center, y_head_center), (x_center, y_center), (0, 255, 0), 2)
                        
                        # Draw keypoints for visualization
                        for kp in keypoints[:5]:  # First 5 keypoints (face)
                            if kp[0] > 0 and kp[1] > 0:
                                cv2.circle(frame, (int(kp[0]), int(kp[1])), 3, (255, 0, 0), -1)

                        # Drone Direction Logic - using actual HEAD size
                        directions = self.drone_directions(x_head_in_square, y_head_in_square, 
                                                          new_w, new_h, head_size)
                        
                        if not control_values['face_detected']:
                            self.fb_velocity = 0
                            self.ud_velocity = 0
                            self.yaw_velocity = 0
                        
                        if self.center:
                            self.yaw_velocity = 0
                            self.ud_velocity = 0
                            print("centered")
                        if self.left:
                            self.yaw_velocity = -15
                            print("turning left")
                        elif self.right:
                            self.yaw_velocity = 15
                            print("turning right")
                        if self.up:
                            self.ud_velocity = 15
                            print("going up")
                        elif self.down:
                            self.ud_velocity = -15
                            print("going down")
                        if self.forward:
                            self.fb_velocity = 15
                            print("going forward")
                        elif self.backward:
                            self.fb_velocity = -15
                            print("going backward")

                if head_detected:
                    cv2.putText(frame, f"Head detected (size: {head_size}px)", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "No head detected", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                if frame_callback:
                    frame_callback(square_frame, control_values)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break     
                    
        except Exception as e:
            print(f'An error occurred: {e}')
            import traceback
            traceback.print_exc()
        finally:
            if cap:
                cap.release()
            cv2.destroyAllWindows()
            print('Camera now closed')

if __name__ == "__main__":
    detector = HeadDetector()
    detector.run_head_detection()