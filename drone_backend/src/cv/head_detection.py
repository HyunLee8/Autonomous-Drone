import cv2
import numpy as np
import mediapipe as mp

def run_head_detection():
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
                cv2.line(square_frame, (x1, 0), (x1, new_h), (255, 0, 0), 2)
                cv2.line(square_frame, (x2, 0), (x2, new_h), (255, 0, 0), 2)
                cv2.line(square_frame, (0, y1), (new_w, y1), (255, 0, 0), 2)
                cv2.line(square_frame, (0, y2), (new_w, y2), (255, 0, 0), 2)
                cv2.circle(square_frame, (new_x_center, new_y_center), 5, (0, 255, 0), -1)
                
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
                        
                        # Draw rectangle around face
                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                        cv2.circle(frame, (x_head_center, y_head_center), 20, (255, 0, 0), -1)
                        cv2.line(frame, (x_head_center, y_head_center), (x_center, y_center), (0, 0, 255), 2)
                    cv2.putText(frame, "Face detected", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
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
    run_head_detection()