# camera.py
import cv2
import threading

# class Camera:
#     def __init__(self, src=0):
#         self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
#         self.lock = threading.Lock()

#         if not self.cap.isOpened():
#             raise RuntimeError("❌ Cannot open camera")

#     def read(self):
#         with self.lock:
#             ret, frame = self.cap.read()
#         return ret, frame

#     def release(self):
#         with self.lock:
#             if self.cap.isOpened():
#                 self.cap.release()

# # GLOBAL SINGLETON
# camera = Camera(0)

class CameraService:
    def __init__(self, cam_id=0):
        self.cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("Camera open failed")

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()
camera = CameraService(0)
