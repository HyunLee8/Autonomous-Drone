class HeadDetector:
    def __init__(self, model_path='face_landmarker.task'):
        self.model_path = model_path
        self.frame_count = 0
        self._initialize_mediapipe()

    def _initialize_mediapipe(self):
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

    def drone_directions(self, x, y, frame_width, frame_height):
        if x < frame_width // 3 and y < frame_height // 3:
            print("up and left")
        elif x > frame_width // 3 and x < (frame_width // 3) * 2 and y < frame_height // 3:
            print("up")
        elif x > (frame_width // 3) * 2 and y < frame_height // 3:
            print("up and right")
        elif x < frame_width // 3 and y > frame_height // 3 and y < (frame_height // 3) * 2:
            print("left")
        elif x > frame_width // 3 and x < (frame_width // 3) * 2 and y > frame_height // 3 and y < (frame_height // 3) * 2:
            print("center")
        elif x > (frame_width // 3) * 2 and y > frame_height // 3 and y < (frame_height // 3) * 2:
            print("right")
        elif x < frame_width // 3 and y > (frame_height // 3) * 2:
            print("down and left")
        elif x > frame_width // 3 and x < (frame_width // 3) * 2 and y > (frame_height // 3) * 2:
            print("down")
        elif x > (frame_width // 3) * 2 and y > (frame_height // 3) * 2:
            print("down and right")

    def run_head_detection(self):
        print("Initializing MediaPipe...")
        
        # Use the new task-based API
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        # Download the model file first if you haven't
        model_path = 'face_landmarker.task'
        
        print("Opening camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print('Error: Could not open camera.')
            return
        
        print("Camera opened successfully!")
        
        # Create FaceLandmarker
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
                    ret, frame = cap.read()
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
                    cv2.rectangle(square_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    #top middle box
                    cv2.rectangle(square_frame, (x2, y1), (x3, y2), (255, 0, 0), 2)
                    #top right box
                    cv2.rectangle(square_frame, (x3, y1), (x4, y2), (255, 0, 0), 2)
                    #middle left box
                    cv2.rectangle(square_frame, (x1, y2), (x2, y3), (255, 0, 0), 2)
                    #middle middle box
                    cv2.rectangle(square_frame, (x2, y2), (x3, y3), (255, 0, 0), 2)
                    #middle right box
                    cv2.rectangle(square_frame, (x3, y2), (x4, y3), (255, 0, 0), 2)
                    #bottom left box
                    cv2.rectangle(square_frame, (x1, y3), (x2, y4), (255, 0, 0), 2)
                    #bottom middle box
                    cv2.rectangle(square_frame, (x2, y3), (x3, y4), (255, 0, 0), 2)
                    #bottom right box
                    cv2.rectangle(square_frame, (x3, y3), (x4, y4), (255, 0, 0), 2)

                    cv2.circle(square_frame, (new_x_center, new_y_center), 20, (0, 255, 0), -1)
                    
                    if not ret:
                        print('Error: Could not read frame.')
                        break
                    
                    frame_count += 1
                    
                    # Convert to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    
                    # Detect face landmarks
                    results = landmarker.detect_for_video(mp_image, frame_count)
                    
                    # Draw bounding box if face detected
                    if results.face_landmarks:
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
                            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                            cv2.circle(frame, (x_head_center, y_head_center), 5, (255, 0, 0), -1)
                            cv2.line(frame, (x_head_center, y_head_center), (x_center, y_center), (0, 0, 255), 2)
                            self.drone_directions(x_head_in_square, y_head_in_square, new_w, new_h)
                        cv2.putText(frame, "Face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "No face detected", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    cv2.imshow('Head Detection', square_frame)
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
    detector.run_head_detection()