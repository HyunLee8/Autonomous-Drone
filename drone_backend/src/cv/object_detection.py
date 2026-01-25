import cv2
from ultralytics import YOLO

def run_model(object_num=0, conf_threshold=0.5):
    model = YOLO("yolo11n.pt")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('Error: could not open video device.')
        return
    
    try:
        while True:
            ret, frame = cap.read() 
            if not ret:
                print('Error: could not read frame from video device.')
                break
            results = model(frame, stream=True, device='mps', conf=conf_threshold)
            for r in results:
                boxes = r.boxes     # gets the coordinates, confidence and class of the detected objects
                frame = r.plot()    # plots the box and labels

            cv2.imshow('YOLOv11n Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except Exception as e:
        print(f'An error occurred: {e}')
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print('camera now closed')
    
if __name__ == "__main__":
    run_model(conf_threshold=0.5)