import cv2
import threading
import time


class CameraService:
    def __init__(self, src=0):
        self.src = src

        # =====================================================
        # OPEN CAMERA (RTSP / HTTP / USB)
        # =====================================================
        self.cap = cv2.VideoCapture(src)

        # giảm buffer để giảm delay
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except:
            pass

        # =====================================================
        # THREAD SAFETY LOCKS
        # =====================================================
        self.lock = threading.Lock()
        self.encode_lock = threading.Lock()

        self.running = True
        self.frame = None
        self.ret = False

        if not self.cap.isOpened():
            print(f"❌ Cannot open camera: {src}")
        else:
            self.ret, self.frame = self.cap.read()

        # =====================================================
        # START BACKGROUND THREAD
        # =====================================================
        self.thread = threading.Thread(
            target=self._update_frame,
            daemon=True
        )
        self.thread.start()

    # =====================================================
    # FRAME CAPTURE LOOP (THREAD SAFE)
    # =====================================================
    def _update_frame(self):
        while self.running:
            try:
                if self.cap.isOpened():
                    ret, frame = self.cap.read()

                    if not ret:
                        print(f"⚠ READ FAIL: {self.src}")
                        time.sleep(0.3)
                        continue

                    with self.lock:
                        self.ret = ret
                        self.frame = frame

                time.sleep(0.01)

            except Exception as e:
                print(f"❌ Camera thread error: {e}")
                time.sleep(0.5)

    # =====================================================
    # AI / LPR / FACE RECOGNITION
    # =====================================================
    def read(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

    # =====================================================
    # FLASK MJPEG STREAM (SAFE ENCODE)
    # =====================================================
    def get_mjpeg_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            frame_copy = self.frame.copy()

        # encode OUTSIDE main lock (CRITICAL FIX)
        with self.encode_lock:
            ret, jpeg = cv2.imencode('.jpg', frame_copy)

        if not ret:
            return None

        return jpeg.tobytes()

    # =====================================================
    # SAFE RELEASE (NO CRASH)
    # =====================================================
    def release(self):
        self.running = False

        try:
            if self.thread.is_alive():
                self.thread.join(timeout=2)
        except:
            pass

        try:
            self.cap.release()
        except:
            pass


# =====================================================
# CAMERA INSTANCES (SMART PARKING SYSTEM)
# =====================================================

ENTRY_STREAM = "http://172.16.10.28:8080/?action=stream"
EXIT_STREAM  = "http://172.16.10.28:8000/stream.mjpg"

entry_camera = CameraService(ENTRY_STREAM)
exit_camera = CameraService(EXIT_STREAM)