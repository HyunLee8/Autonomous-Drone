import cv2
import numpy as np
import mediapipe as mp
import os
from src.tello import Tello

class HeadDetector:
    def __init__(self, model_path=None):
        if model_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'face_landmarker.task')

        self.model_path = model_path
        self.frame_count = 0
        self._initialize_mediapipe()
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

    def _initialize_mediapipe(self):
        # Add this debug line
        print(f"Loading model from: {self.model_path}")
        print(f"Model exists: {os.path.exists(self.model_path)}")

        mp.tasks = mp.tasks
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = FaceLandmarker.create_from_options(options)

    def drone_directions(self, x, y, frame_width, frame_height, face_size, forward_threshold=300, backward_threshold=350):
        if x < frame_width // 3 and y < frame_height // 3:
            if face_size < forward_threshold:
                self.up, self.left, self.forward = True, True, True
                self.down, self.right, self.backward, self.center = False, False, False, False
            elif face_size > backward_threshold:
                self.up, self.left, self.backward = True, True, True
                self.down, self.right, self.forward, self.center = False, False, False, False
            else:
                self.up, self.left = True, True
                self.down, self.right, self.backward, self.forward, self.center = False, False, False, False, False
        elif x > frame_width // 3 and x < (frame_width // 3) * 2 and y < frame_height // 3:
            if face_size < forward_threshold:
                self.up, self.forward = True, True
                self.down, self.left, self.right, self.backward, self.center = False, False, False, False, False
            elif face_size > backward_threshold:
                self.up, self.backward = True, True
                self.down, self.left, self.right, self.forward, self.center = False, False, False, False, False
            else:
                self.up = True
                self.down, self.left, self.right, self.backward, self.forward, self.center = False, False, False, False, False, False
        elif x > (frame_width // 3) * 2 and y < frame_height // 3:
            if face_size < forward_threshold:
                self.up, self.right, self.forward = True, True, True
                self.down, self.left, self.backward, self.center = False, False, False, False
            elif face_size > backward_threshold:
                self.up, self.right, self.backward = True, True, True
                self.down, self.left, self.forward, self.center = False, False, False, False
            else:
                self.up, self.right = True, True
                self.down, self.left, self.backward, self.center, self.forward = False, False, False, False, False
        elif x < frame_width // 3 and y > frame_height // 3 and y < (frame_height // 3) * 2:
            if face_size < forward_threshold:
                self.left, self.forward = True, True
                self.right, self.center, self.up, self.down, self.backward = False, False, False, False, False
            elif face_size > backward_threshold:
                self.left, self.backward = True, True
                self.right, self.center, self.up, self.down, self.forward = False, False, False, False, False
            else:
                self.left = True
                self.right, self.center, self.up, self.down, self.backward, self.forward = False, False, False, False, False, False
        elif x > frame_width // 3 and x < (frame_width // 3) * 2 and y > frame_height // 3 and y < (frame_height // 3) * 2:
            if face_size < forward_threshold:
                self.center, self.forward = True, True
                self.left, self.right, self.up, self.down, self.backward = False, False, False, False, False
            elif face_size > backward_threshold:
                self.center, self.backward = True, True
                self.left, self.right, self.up, self.down, self.forward = False, False, False, False, False
            else:
                self.center = True
                self.left, self.right, self.up, self.down, self.backward, self.forward = False, False, False, False, False, False
        elif x > (frame_width // 3) * 2 and y > frame_height // 3 and y < (frame_height // 3) * 2:
            if face_size < forward_threshold:
                self.right, self.forward = True, True
                self.left, self.center, self.up, self.down, self.backward = False, False, False, False, False
            elif face_size > backward_threshold:
                self.right, self.backward = True, True
                self.left, self.center, self.up, self.down, self.forward = False, False, False, False, False
            else:
                self.right = True
                self.left, self.center, self.up, self.down, self.backward, self.forward = False, False, False, False, False, False
        elif x < frame_width // 3 and y > (frame_height // 3) * 2:
            if face_size < forward_threshold:
                self.down, self.left, self.forward = True, True, True
                self.up, self.right, self.backward, self.center = False, False, False, False
            elif face_size > backward_threshold:
                self.down, self.left, self.backward = True, True, True
                self.up, self.right, self.forward, self.center = False, False, False, False
            else:
                self.down, self.left = True, True
                self.up, self.right, self.backward, self.center, self.forward = False, False, False, False, False
        elif x > frame_width // 3 and x < (frame_width // 3) * 2 and y > (frame_height // 3) * 2:
            if face_size < forward_threshold:
                self.down, self.forward = True, True
                self.up, self.left, self.right, self.backward, self.center = False, False, False, False, False
            elif face_size > backward_threshold:
                self.down, self.backward = True, True
                self.up, self.left, self.right, self.forward, self.center = False, False, False, False, False
            else:
                self.down = True
                self.up, self.left, self.right, self.backward, self.center, self.forward = False, False, False, False, False, False
        elif x > (frame_width // 3) * 2 and y > (frame_height // 3) * 2:
            if face_size < forward_threshold:
                self.down, self.right, self.forward = True, True, True
                self.up, self.left, self.backward, self.center = False, False, False, False
            elif face_size > backward_threshold:
                self.down, self.right, self.backward = True, True, True
                self.up, self.left, self.forward, self.center = False, False, False, False
            else:
                self.down, self.right = True, True
                self.up, self.left, self.backward, self.center, self.forward = False, False, False, False, False

    def FoundHead(self, frame):
        try:
            rbg_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rbg_frame)
            self.frame_count += 1
            results = self.landmarker.detect_for_video(mp_image, self.frame_count)
            return len(results.face_landmarks) > 0
        except Exception as e:
            print(f'Error in FoundHead: {e}')
            return False

    def run_head_detection(self, frame_callback=None, stop_flag=None, send_commands=False):
        print("Initializing MediaPipe...")

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        model_path = self.model_path
        print("Opening camera...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print('Error: Could not open camera.')
            return
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        with FaceLandmarker.create_from_options(options) as landmarker:
            print("Starting detection loop... Press 'q' to quit")

            frame_count = 0
            try:
                while True:
                    if stop_flag and stop_flag.is_set():  # ← Checks flag every iteration
                        break 
                    ret, frame = cap.read()
                    if not ret:
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


                    #x cords
                    x1, x2, x3, x4 = 0, x1, x2, new_w
                    #y cords
                    y1, y2, y3, y4 = 0, y1, y2, new_h

                    #top left box
                    cv2.rectangle(square_frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                    #top middle box
                    cv2.rectangle(square_frame, (x2, y1), (x3, y2), (255, 255, 255), 2)
                    #top right box
                    cv2.rectangle(square_frame, (x3, y1), (x4, y2), (255, 255, 255), 2)
                    #middle left box
                    cv2.rectangle(square_frame, (x1, y2), (x2, y3), (255, 255, 255), 2)
                    #middle middle box
                    cv2.rectangle(square_frame, (x2, y2), (x3, y3), (255, 255, 255), 2)
                    #middle right box
                    cv2.rectangle(square_frame, (x3, y2), (x4, y3), (255, 255, 255), 2)
                    #bottom left box
                    cv2.rectangle(square_frame, (x1, y3), (x2, y4), (255, 255, 255), 2)
                    #bottom middle box
                    cv2.rectangle(square_frame, (x2, y3), (x3, y4), (255, 255, 255), 2)
                    #bottom right box
                    cv2.rectangle(square_frame, (x3, y3), (x4, y4), (255, 255, 255), 2)

                    cv2.circle(square_frame, (new_x_center, new_y_center), 20, (255, 255, 255), -1)

                    frame_count += 1

                    # Convert to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    results = landmarker.detect_for_video(mp_image, frame_count)

                    # Initialize control values
                    control_values = {
                        #'lr_velocity': 0,      # left/right (not used, always 0)
                        #'fb_velocity': 0,      # forward/backward
                        #'ud_velocity': 0,      # up/down
                        #'yaw_velocity': 0,     # rotation
                        'face_detected': False
                    }

                    # Draw bounding box if face detected
                    if results.face_landmarks:
                        control_values['face_detected'] = True

                        for face_landmarks in results.face_landmarks:
                            # Get all x and y coordinates
                            x_coords = [landmark.x * frame.shape[1] for landmark in face_landmarks]
                            y_coords = [landmark.y * frame.shape[0] for landmark in face_landmarks]

                            # Calculate bounding box
                            x_min = int(min(x_coords))
                            x_max = int(max(x_coords))
                            y_min = int(min(y_coords))
                            y_max = int(max(y_coords))
                            x_head_center = (x_min + x_max) // 2
                            y_head_center = (y_min + y_max) // 2

                            x_head_in_square = x_head_center - (x_center - radius)
                            y_head_in_square = y_head_center

                            # Draw rectangle around face
                            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 255, 255), 2)
                            cv2.circle(frame, (x_head_center, y_head_center), 5, (255, 255, 255), -1)
                            cv2.line(frame, (x_head_center, y_head_center), (x_center, y_center), (0, 0, 0), 2)

                            #Drone Direction Logic
                            x_error = x_head_in_square - new_x_center
                            y_error = y_head_in_square - new_y_center
                            yaw_velocity = 0
                            ud_velocity = 0
                            fb_velocity = 0
                            directions = self.drone_directions(x_head_in_square, y_head_in_square, new_w, new_h, x_max-x_min)
                            if self.center:
                                yaw_velocity = 0
                                ud_velocity = 0
                                print("centered")
                            if self.left:
                                yaw_velocity = -30
                                print("turning left")
                            elif self.right:
                                lr_velocity = 30
                                print("turning right")
                            if self.up:
                                ud_velocity = 30
                                print("going up")
                            elif self.down:
                                ud_velocity = -30
                                print("going down")
                            if self.forward:
                                fb_velocity = 30
                                print("going forward")
                            elif self.backward:
                                fb_velocity = -30
                                print("going backward")

                            cv2.putText(frame, "Face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "No face detected", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    if frame_callback:
                        frame_callback(square_frame, control_values)
                    #cv2.imshow('Head Detection', square_frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break     
            except Exception as e:
                print(f'An error occurred: {e}')
                import traceback
                traceback.print_exc()
            finally:
                cap.release()
                cv2.destroyAllWindows()
                print('Camera now closed')

if __name__ == "__main__":
    detector = HeadDetector()