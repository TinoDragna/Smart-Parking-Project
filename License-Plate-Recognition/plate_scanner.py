from PIL import Image
import cv2
import torch
import torch_patch
import os
import time
from datetime import datetime
from collections import defaultdict
from camera import entry_camera, exit_camera

import function.utils_rotate as utils_rotate
import function.helper as helper

# ===============================
# 📌 CONFIG
# ===============================
FULL_CROP_PATH = "../smart_parking_data/full_crop_LP"
os.makedirs(FULL_CROP_PATH, exist_ok=True)

MIN_CROP_PATH = "../smart_parking_data/min_crop_LP"
os.makedirs(MIN_CROP_PATH, exist_ok=True)

# ===============================
# 📌 Stable Plate Tracking Logic
# ===============================
class PlateTracker:
    def __init__(self, stable_interval=10, min_count=3):
        """
        stable_interval: thời gian gom OCR (giây)
        min_count: số lần giống nhau để chấp nhận
        """
        self.stable_interval = stable_interval
        self.min_count = min_count
        self.plate_records = defaultdict(list)

    def add_plate(self, plate_text):
        now = time.time()
        self.plate_records[plate_text].append(now)

        # loại timestamp cũ
        for p in list(self.plate_records.keys()):
            self.plate_records[p] = [
                t for t in self.plate_records[p]
                if now - t <= self.stable_interval
            ]
            if not self.plate_records[p]:
                del self.plate_records[p]

        best_plate = max(self.plate_records, key=lambda k: len(self.plate_records[k]))
        best_count = len(self.plate_records[best_plate])

        if best_count >= self.min_count:
            return best_plate

        return None

# ===============================
# 📌 Load YOLO models
# ===============================
yolo_LP_detect = torch.hub.load(
    'yolov5', 'custom',
    path='model/LP_detector_nano_61.pt',
    source='local'
)

yolo_license_plate = torch.hub.load(
    'yolov5', 'custom',
    path='model/LP_ocr_nano_62.pt',
    source='local'
)
yolo_license_plate.conf = 0.4

# ===============================
# 📌 Scan Plate (NO WINDOW)
# ===============================
def scan_plate(camera_obj=None, timeout=20):
    """
    Trả về ngay khi detect được biển hợp lệ
    KHÔNG mở cửa sổ camera
    """
    if camera_obj is None:
        camera_obj = entry_camera
    
    tracker = PlateTracker(stable_interval=10, min_count=1)
    start_time = time.time()

    print("📸 scan_plate: START")

    for _ in range(10):
        camera_obj.read()
        time.sleep(0.01)

    if hasattr(camera_obj, 'read'):
        use_cam_service = True
    else:
        use_cam_service = False
        cap = cv2.VideoCapture(camera_obj)

    while time.time() - start_time < timeout:
        if use_cam_service:
            ret, frame = camera_obj.read()
        else:
            ret, frame = cap.read()

        if not ret or frame is None:
            continue

        plates = yolo_LP_detect(frame, size=640)
        detections = plates.pandas().xyxy[0].values.tolist()

        for plate in detections:
            x1, y1, x2, y2 = map(int, plate[:4])
            crop_img = frame[y1:y2, x1:x2]
            if crop_img.size == 0:
                continue

            detected_text = "unknown"

            for cc in range(2):
                for ct in range(2):
                    text = helper.read_plate(
                        yolo_license_plate,
                        utils_rotate.deskew(crop_img, cc, ct)
                    )
                    if text != "unknown":
                        detected_text = text
                        break
                if detected_text != "unknown":
                    break

            if detected_text != "unknown":
                confirmed_plate = tracker.add_plate(detected_text)

                if confirmed_plate:
                    ts = datetime.now().strftime("%d%m%Y_%H%M%S")
                    full_crop_path = os.path.join(
                        FULL_CROP_PATH, f"{confirmed_plate}_{ts}.jpg"
                    )
                    min_crop_path = os.path.join(
                        MIN_CROP_PATH, f"{confirmed_plate}_{ts}.jpg"
                    )

                    cv2.imwrite(full_crop_path, frame)
                    cv2.imwrite(min_crop_path, crop_img)

                    print(f"✅ LPR OK: {confirmed_plate}")
                    if not use_cam_service:
                        cap.release()
                    return full_crop_path, min_crop_path, confirmed_plate
    
    if not use_cam_service:
        cap.release()
    print("⚠ LPR TIMEOUT")
    return None, None, None


# ===============================
# TEST
# ===============================
if __name__ == "__main__":
    f, m, p = scan_plate()
    print("FULL:", f)
    print("MIN :", m)
    print("PLATE:", p)