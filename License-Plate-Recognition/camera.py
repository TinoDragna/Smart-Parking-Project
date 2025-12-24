# camera.py
import cv2
import threading
import time

class CameraService:
    def __init__(self, cam_id=0):   #0 là cam máy, 1 là ngoại vi
        self.cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("Camera open failed")
        self.lock = threading.Lock()

    def read(self):
        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ Camera read failed")
                time.sleep(0.2)
            return ret, frame

    def release(self):
        with self.lock:
            self.cap.release()

camera = CameraService(0)
