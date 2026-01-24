"""
Won't use for now but if initial calibration is bad
then will have to add extra steps to align drone in the air 
however I don't think this will be necessary
"""

import cv2
import numpy as np

class ArucoDetector:
    def __init__(self, marker_size=6):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
    
    def detect(self, frame, target_marker_id):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)

        if ids is not None and target_marker_id in ids:
            # Find the target marker
            idx = np.where(ids == target_marker_id)[0][0]
            corner = corners[idx][0]
            
            # Calculate center
            center_x = np.mean(corner[:, 0]) / frame.shape[1]
            center_y = np.mean(corner[:, 1]) / frame.shape[0]
            
            # Calculate size (area as percentage of frame)
            area = cv2.contourArea(corner)
            frame_area = frame.shape[0] * frame.shape[1]
            size = area / frame_area
            
            return (center_x, center_y, size)
        
        return None