import cv2
import threading
import time

class CameraService:
    def __init__(self, src=0): # Thay src=0 bằng URL camera (ví dụ: 'rtsp://...') nếu dùng IP Cam
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.lock = threading.Lock() # Lock để chống Race Condition
        self.running = True
        
        if not self.cap.isOpened():
            print("❌ Không thể mở Camera!")
            self.ret = False
            self.frame = None
        else:
            self.ret, self.frame = self.cap.read()
            
        # Khởi chạy luồng phụ (background thread) liên tục đọc frame
        self.thread = threading.Thread(target=self._update_frame, daemon=True)
        self.thread.start()

    def _update_frame(self):
        """Liên tục lấy khung hình mới nhất từ Camera lưu vào biến cục bộ."""
        while self.running:
            if self.cap.isOpened():

                for _ in range(3):
                    self.cap.grab()

                ret, frame = self.cap.retrieve()

                with self.lock:
                    self.ret = ret
                    self.frame = frame

            time.sleep(0.01)

    def read(self):
        """Dùng cho AI (LPR, DeepFace) lấy frame OpenCV thô."""
        with self.lock:
            if self.frame is not None:
                # Trả về bản copy để AI xử lý không ảnh hưởng tới frame gốc đang stream
                return self.ret, self.frame.copy()
            return self.ret, None

    def get_mjpeg_frame(self):
        """Dùng cho Flask Web Server lấy ảnh JPEG để stream."""
        with self.lock:
            if self.frame is None:
                return None
            # Nén frame OpenCV thành chuẩn JPEG
            ret, jpeg = cv2.imencode('.jpg', self.frame)
            if not ret:
                return None
            return jpeg.tobytes()

    def release(self):
        """Dọn dẹp và tắt camera an toàn."""
        self.running = False
        self.thread.join() # Đợi luồng phụ kết thúc
        self.cap.release()

# Khởi tạo instance toàn cục để import vào các file khác
# camera = CameraService(0) # Khai báo tham số src tương ứng của bạn
ENTRY_STREAM = "https://iot.eiu.com.vn/pi5/?action=stream"
EXIT_STREAM  = "https://iot.eiu.com.vn/pi5Picam/stream.mjpg"

entry_camera = CameraService(ENTRY_STREAM)
exit_camera = CameraService(EXIT_STREAM)