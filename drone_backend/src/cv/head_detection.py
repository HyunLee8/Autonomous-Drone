import cv2
import numpy as np
from ultralytics import YOLO
import os
import time
from collections import deque

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
        
        # Direction flags
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.forward = False
        self.backward = False
        self.center = False
        self.lr_velocity = 0
        self.fb_velocity = 0
        self.ud_velocity = 0
        self.yaw_velocity = 0
        self.position_buffer = deque(maxlen=5)
        self.size_buffer = deque(maxlen=5)
        self.skip_frames = 2
        self.current_frame_skip = 0
        self.last_detection = None
    
        self.velocity_alpha = 0.3 
        

        self.head_size_forward_threshold = 100  
        self.head_size_backward_threshold = 125 

    def _initialize_yolo(self):
        """Initialize YOLO pose model for head detection"""
        print(f"Loading YOLO pose model: {self.model_path}")
        self.model = YOLO(self.model_path)
        self.model.fuse()
        print("YOLO pose model loaded successfully")

    def _smooth_position(self, x, y, size):
        """Apply temporal smoothing to reduce jitter"""
        self.position_buffer.append((x, y))
        self.size_buffer.append(size)
        
        if len(self.position_buffer) < 3:
            return x, y, size
        
        weights = np.array([0.2, 0.3, 0.5])
        positions = np.array(list(self.position_buffer)[-3:])
        sizes = np.array(list(self.size_buffer)[-3:])
        
        smooth_x = int(np.average(positions[:, 0], weights=weights))
        smooth_y = int(np.average(positions[:, 1], weights=weights))
        smooth_size = int(np.average(sizes, weights=weights))
        
        return smooth_x, smooth_y, smooth_size

    def _smooth_velocity(self, target_velocity, current_velocity):
        """Smooth velocity changes to prevent jerky movements"""
        return self.velocity_alpha * target_velocity + (1 - self.velocity_alpha) * current_velocity

    def drone_directions(self, x, y, frame_width, frame_height, face_size):
        """Determine drone movement directions with optimized logic"""
        center_x = frame_width // 2
        center_y = frame_height // 2
        distance_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        deadzone_radius = frame_width // 12 
    
        self.left = self.right = self.up = self.down = False
        self.forward = self.backward = self.center = False
        
        target_yaw = 0
        target_ud = 0
        target_fb = 0
        
        optimal_size = (self.head_size_forward_threshold + self.head_size_backward_threshold) / 2
        size_range = self.head_size_backward_threshold - self.head_size_forward_threshold
        
        if distance_from_center < deadzone_radius:
            self.center = True
            target_yaw = 0
            target_ud = 0
            
            if face_size < self.head_size_forward_threshold:
                self.forward = True
                distance_from_threshold = (self.head_size_forward_threshold - face_size) / self.head_size_forward_threshold
                target_fb = int(5 + (15 * min(distance_from_threshold, 1.0)))
            elif face_size > self.head_size_backward_threshold:
                self.backward = True
                distance_from_threshold = (face_size - self.head_size_backward_threshold) / self.head_size_backward_threshold
                target_fb = -int(5 + (15 * min(distance_from_threshold, 1.0)))
            else:
                target_fb = 0
        else:
            intensity = min(distance_from_center / deadzone_radius, 2.0)
            
            dx = x - center_x
            if abs(dx) > 20:
                if dx < 0:
                    self.left = True
                    target_yaw = -int(20 * min(intensity, 1.5))
                else:
                    self.right = True
                    target_yaw = int(20 * min(intensity, 1.5))
            
            dy = y - center_y
            if abs(dy) > 20:
                if dy < 0:
                    self.up = True
                    target_ud = int(20 * min(intensity, 1.5))
                else:
                    self.down = True
                    target_ud = -int(20 * min(intensity, 1.5))
            
            if face_size < self.head_size_forward_threshold:
                self.forward = True
                distance_from_threshold = (self.head_size_forward_threshold - face_size) / self.head_size_forward_threshold
                target_fb = int(5 + (15 * min(distance_from_threshold, 1.0)))
            elif face_size > self.head_size_backward_threshold:
                self.backward = True
                distance_from_threshold = (face_size - self.head_size_backward_threshold) / self.head_size_backward_threshold
                target_fb = -int(5 + (15 * min(distance_from_threshold, 1.0)))
        
    
        self.yaw_velocity = int(self._smooth_velocity(target_yaw, self.yaw_velocity))
        self.ud_velocity = int(self._smooth_velocity(target_ud, self.ud_velocity))
        self.fb_velocity = int(self._smooth_velocity(target_fb, self.fb_velocity))
        
    
        if abs(self.yaw_velocity) < 3:
            self.yaw_velocity = 0
        if abs(self.ud_velocity) < 3:
            self.ud_velocity = 0
        if abs(self.fb_velocity) < 3:
            self.fb_velocity = 0

    def FoundHead(self, frame):
        """Quick check if a head is detected - optimized version"""
        try:
            small_frame = cv2.resize(frame, (320, 240))
            results = self.model(small_frame, verbose=False, conf=0.3, imgsz=320)
            
            if results[0].keypoints is not None and len(results[0].keypoints) > 0:
                return True
            return False
        except Exception as e:
            print(f'Error in FoundHead: {e}')
            return False

    def run_head_detection(self, frame_callback=None, stop_flag=None, send_commands=False):
        """Main detection loop - optimized version"""
        print("Initializing YOLO pose detection...")
        drone = self.drone

        cap = None

        if drone is not None:
            print("Using Tello camera...")
            print("Waiting for drone video stream...")
            
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
            # Set camera resolution for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            def get_frame():
                ret, frame = cap.read()
                return frame if ret else None

        print("Starting detection loop... Press 'q' to quit")

        fps_time = time.time()
        fps_counter = 0
        current_fps = 0

        try:
            while True:
                if stop_flag and stop_flag.is_set():
                    break 
                    
                frame = get_frame()
                if frame is None:
                    print('Error: Could not read frame.')
                    break

                # FPS calculation
                fps_counter += 1
                if time.time() - fps_time > 1:
                    current_fps = fps_counter
                    fps_counter = 0
                    fps_time = time.time()

                h, w, _ = frame.shape
                x_center = w // 2
                y_center = h // 2
                radius = h // 2

                square_frame = frame[0:h, x_center - radius : x_center + radius]
                new_h, new_w, _ = square_frame.shape

                new_x_center, new_y_center = new_w // 2, new_h // 2
                deadzone_radius = new_w // 8  # MUCH SMALLER deadzone (was // 4)
                
                grid_color = (100, 100, 100)  # Subtle gray
                x_third = new_w // 3
                y_third = new_h // 3
                
                cv2.line(square_frame, (x_third, 0), (x_third, new_h), grid_color, 1)
                cv2.line(square_frame, (x_third * 2, 0), (x_third * 2, new_h), grid_color, 1)
                
                cv2.line(square_frame, (0, y_third), (new_w, y_third), grid_color, 1)
                cv2.line(square_frame, (0, y_third * 2), (new_w, y_third * 2), grid_color, 1)
                
                cv2.circle(square_frame, (new_x_center, new_y_center), deadzone_radius, (0, 255, 255), 2)
                
                cv2.circle(square_frame, (new_x_center, new_y_center), 5, (0, 255, 255), -1)
                
                cv2.circle(square_frame, (new_x_center, new_y_center), deadzone_radius, (0, 255, 0), 1)
                cv2.rectangle(square_frame, (0, 0), (new_w-1, new_h-1), (255, 255, 255), 2)
                
                control_values = {'face_detected': False}
                head_detected = False
                
                self.current_frame_skip += 1
                if self.current_frame_skip >= self.skip_frames or self.last_detection is None:
                    self.current_frame_skip = 0
                    
                    results = self.model(frame, verbose=False, conf=0.3, imgsz=640)

                    if results[0].keypoints is not None and len(results[0].keypoints) > 0:
                        keypoints = results[0].keypoints.xy[0].cpu().numpy()
                        
                        nose = keypoints[0]
                        left_eye = keypoints[1]
                        right_eye = keypoints[2]
                        
                        if nose[0] > 0 and nose[1] > 0:
                            head_detected = True
                            control_values['face_detected'] = True
                            
                            x_head_center = int(nose[0])
                            y_head_center = int(nose[1])
                            
                            # Calculate head size
                            if left_eye[0] > 0 and right_eye[0] > 0:
                                eye_distance = np.sqrt((right_eye[0] - left_eye[0])**2 + 
                                                      (right_eye[1] - left_eye[1])**2)
                                head_width_multiplier = 2.0
                                head_size = int(eye_distance * head_width_multiplier)
                            else:
                                head_size = 100
                            
                            # Apply smoothing
                            x_head_in_square = x_head_center - (x_center - radius)
                            y_head_in_square = y_head_center
                            
                            smooth_x, smooth_y, smooth_size = self._smooth_position(
                                x_head_in_square, y_head_in_square, head_size
                            )
                            
                            # Cache detection for frame skipping
                            self.last_detection = {
                                'x': x_head_center,
                                'y': y_head_center,
                                'x_square': smooth_x,
                                'y_square': smooth_y,
                                'size': smooth_size,
                                'keypoints': keypoints
                            }
                else:
                    # Use cached detection for skipped frames
                    if self.last_detection:
                        head_detected = True
                        control_values['face_detected'] = True
                        x_head_center = self.last_detection['x']
                        y_head_center = self.last_detection['y']
                        smooth_x = self.last_detection['x_square']
                        smooth_y = self.last_detection['y_square']
                        smooth_size = self.last_detection['size']
                        keypoints = self.last_detection['keypoints']

                if head_detected and self.last_detection:
                    half_size = smooth_size // 2
                    x_min = x_head_center - half_size
                    x_max = x_head_center + half_size
                    y_min = y_head_center - half_size
                    y_max = y_head_center + half_size
                    
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
                    cv2.circle(frame, (x_head_center, y_head_center), 5, (0, 255, 0), -1)
                    cv2.line(frame, (x_head_center, y_head_center), (x_center, y_center), (0, 255, 0), 2)
                    
                    for kp in keypoints[:5]:
                        if kp[0] > 0 and kp[1] > 0:
                            cv2.circle(frame, (int(kp[0]), int(kp[1])), 3, (255, 0, 0), -1)

                    self.drone_directions(smooth_x, smooth_y, new_w, new_h, smooth_size)
                    
                    status_text = []
                    if self.center:
                        status_text.append("CENTERED")
                    if self.left:
                        status_text.append(f"LEFT (yaw:{self.yaw_velocity})")
                    if self.right:
                        status_text.append(f"RIGHT (yaw:{self.yaw_velocity})")
                    if self.up:
                        status_text.append(f"UP (ud:{self.ud_velocity})")
                    if self.down:
                        status_text.append(f"DOWN (ud:{self.ud_velocity})")
                    if self.forward:
                        status_text.append(f"FWD (fb:{self.fb_velocity})")
                    if self.backward:
                        status_text.append(f"BACK (fb:{self.fb_velocity})")
                    
                    cv2.putText(frame, f"Head: {smooth_size}px | {' | '.join(status_text)}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    # Reset velocities when no detection
                    self.fb_velocity = 0
                    self.ud_velocity = 0
                    self.yaw_velocity = 0
                    cv2.putText(frame, "No head detected", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Display FPS
                cv2.putText(frame, f"FPS: {current_fps}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

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