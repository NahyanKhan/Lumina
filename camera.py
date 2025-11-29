import cv2
import numpy as np

class SpectralCamera:
    def __init__(self, source=0):
        # Initialize the Webcam (0 is usually the default camera)
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise ValueError("Could not open webcam. Ensure no other app is using it.")

    def get_frame(self):
        """
        Captures a single frame and converts it to RGB for processing.
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # OpenCV defaults to BGR, but we need RGB for calculations later
        # However, for the 'physics' subtraction, BGR is fine as long as we differencing the right channels.
        # Let's keep it standard BGR here to match physics.py expectations.
        return frame

    def release(self):
        """
        Releases the hardware lock.
        """
        self.cap.release()
