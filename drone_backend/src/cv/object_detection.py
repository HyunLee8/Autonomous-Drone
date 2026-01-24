import cv2
from ultralytics import YOLO

def run_model(object_num=0, conf_threshold=0.5):
    model = YOLO("yolo11n.pt")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('Error: could not open video device.')
        return

def run_model(object_num=0, conf_threshold=0.5):
    if not ret:
        print('Error: could not read frame from video device.')
        break
    results = model(frame, stream=True, device='mps', conf=conf_threshold)
    for r in results:
        boxes = r.boxes 
        frame = r.plot() 

def run_model(object_num=0, conf_threshold=0.5):
        print('camera now closed')

if __name__ == "__main__":
    run_model(conf_threshold=0.5)