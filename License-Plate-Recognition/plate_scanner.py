from PIL import Image
import cv2
import torch_patch
import torch
import os
import time
import math
from collections import defaultdict

import function.utils_rotate as utils_rotate
import function.helper as helper

# ===============================
# 📌 CONFIG
# ===============================
SAVE_PATH = "../smart_parking_data/license_plate"
os.makedirs(SAVE_PATH, exist_ok=True)
# ----------- For colect dataset
SAVE_PATH_crop_LP = "../smart_parking_data/just_license_plate"
os.makedirs(SAVE_PATH_crop_LP, exist_ok=True)

# ===============================
# 📌 Stable Plate Tracking Logic
# ===============================
class PlateTracker:
    def __init__(self, stable_interval=10, min_count=3, clear_interval=0):
        """
        stable_interval: thời gian gom dữ liệu OCR (mặc định 10s)
        min_count: số lần xuất hiện giống nhau để chấp nhận (mặc định >=3 lần)
        clear_interval: xóa biển cũ khỏi bộ nhớ (mặc định 10 phút)
        """
        self.stable_interval = stable_interval
        self.min_count = min_count
        self.clear_interval = clear_interval

        self.plate_records = defaultdict(list)  # {plate_text: [timestamps]}
        self.saved_plates = {}  # {plate: last_saved_time}

    def add_plate(self, plate_text):
        now = time.time()
        self.plate_records[plate_text].append(now)

        # Remove outdated values
        for p in list(self.plate_records.keys()):
            self.plate_records[p] = [t for t in self.plate_records[p] if now - t <= self.stable_interval]
            if not self.plate_records[p]:
                del self.plate_records[p]

        # Check top candidate plate
        if self.plate_records:
            best_plate = max(self.plate_records, key=lambda k: len(self.plate_records[k]))
            best_count = len(self.plate_records[best_plate])

            if best_count >= self.min_count and best_plate not in self.saved_plates:
                self.saved_plates[best_plate] = now
                print(f"📌 Plate confirmed: {best_plate} ({best_count} detections)")
                return best_plate  # → báo lưu
        return None

    def cleanup_saved(self):
        now = time.time()
        expired = [p for p, t in self.saved_plates.items() if now - t > self.clear_interval]
        for p in expired:
            print(f"🧹 Cleaned expired plate: {p}")
            del self.saved_plates[p]

# ===============================
# 📌 Load YOLO models
# ===============================
yolo_LP_detect = torch.hub.load('yolov5', 'custom', path='model/LP_detector_nano_61.pt', source='local')
yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr_nano_62.pt', source='local')
yolo_license_plate.conf = 0.60

tracker = PlateTracker(stable_interval=10, min_count=3)

# ===============================
# 📌 Webcam Loop
# ===============================
def scan_plate():
    vid = cv2.VideoCapture(0)
    if not vid.isOpened():
        print("❌ Cannot open cam")
        exit()
    prev_frame_time = 0

    while True:
        ret, frame = vid.read()
        if not ret:
            continue

        plates = yolo_LP_detect(frame, size=640)
        detections = plates.pandas().xyxy[0].values.tolist()

        for plate in detections:
            x1, y1, x2, y2 = map(int, plate[:4])
            crop_img = frame[y1:y2, x1:x2]

            # Try OCR rotations
            detected_text = "unknown"
            for cc in range(2):
                for ct in range(2):
                    text = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                    if text != "unknown":
                        detected_text = text
                        break
                if detected_text != "unknown":
                    break

            if detected_text != "unknown":
                confirmed_plate = tracker.add_plate(detected_text)

                # Only save once when confirmed
                if confirmed_plate:
                    timestamp = str(int(time.time()))
                    file_path = os.path.join(SAVE_PATH, f"{confirmed_plate}_{timestamp}.jpg")
                    file_path_2 = os.path.join(SAVE_PATH_crop_LP, f"{confirmed_plate}_{timestamp}.jpg")
                    cv2.imwrite(file_path, crop_img)
                    cv2.imwrite(file_path_2, frame)

                    print(f"✅ SAVED: {confirmed_plate} → {file_path}")

                    vid.release()
                    cv2.destroyAllWindows()
                    return file_path, file_path_2, confirmed_plate

        # FPS Display
        now = time.time()
        fps = int(1 / (now - prev_frame_time)) if prev_frame_time else 0
        prev_frame_time = now

        cv2.putText(frame, f"FPS: {fps}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("License Plate Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    vid.release()
    cv2.destroyAllWindows()
    return None, None, None


# ========== TEST RUN ==========
if __name__ == "__main__":
    img_path, just_LP, plate = scan_plate()
    print("\n------------------------------")
    print("📁 Saved Image:", img_path)
    print("🔍 Detected Plate:", plate)
