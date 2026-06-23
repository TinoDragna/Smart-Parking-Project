import cv2
import time
import os
from datetime import datetime
from collections import defaultdict

import torch
import torch_patch

from camera import entry_camera, exit_camera

import function.utils_rotate as utils_rotate
import function.helper as helper

# ===============================
# CONFIG
# ===============================
FULL_CROP_PATH = "../smart_parking_data/full_crop_LP"
MIN_CROP_PATH = "../smart_parking_data/min_crop_LP"

os.makedirs(FULL_CROP_PATH, exist_ok=True)
os.makedirs(MIN_CROP_PATH, exist_ok=True)

# ===============================
# YOLO MODELS
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
# PLATE STABILIZER (FIXED)
# ===============================
class PlateTracker:
    def __init__(self, window_sec=3, min_votes=3):
        self.window_sec = window_sec
        self.min_votes = min_votes
        self.buffer = []

    def add(self, plate):
        now = time.time()
        self.buffer.append((plate, now))

        # giữ dữ liệu 3 giây gần nhất
        self.buffer = [
            x for x in self.buffer
            if now - x[1] <= self.window_sec
        ]

        # vote
        votes = {}
        for p, _ in self.buffer:
            votes[p] = votes.get(p, 0) + 1

        best = max(votes, key=votes.get)
        if votes[best] >= self.min_votes:
            return best

        return None


# ===============================
# SAFE CROP (FIX IMPORTANT)
# ===============================
def safe_crop(frame, x1, y1, x2, y2):
    h, w = frame.shape[:2]

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    if x2 <= x1 or y2 <= y1:
        return None

    return frame[y1:y2, x1:x2]


# ===============================
# OCR SINGLE PASS (FIX MAJOR BUG)
# ===============================
def ocr_plate(crop_img):
    try:
        # chỉ 1 pass → tránh nhiễu
        text = helper.read_plate(
            yolo_license_plate,
            utils_rotate.deskew(crop_img, 0, 0)
        )
        return text
    except:
        return "unknown"


# ===============================
# MAIN FUNCTION
# ===============================
def scan_plate(camera_obj=None, timeout=15):
    if camera_obj is None:
        camera_obj = entry_camera

    tracker = PlateTracker(window_sec=3, min_votes=3)

    print("📸 LPR START")

    # warmup camera
    for _ in range(5):
        camera_obj.read()
        time.sleep(0.02)

    start = time.time()

    while time.time() - start < timeout:
        ret, frame = camera_obj.read()
        if not ret or frame is None:
            continue

        frame = frame.copy()

        # DETECT PLATE
        results = yolo_LP_detect(frame, size=640)
        detections = results.pandas().xyxy[0].values.tolist()

        for det in detections:
            x1, y1, x2, y2 = map(int, det[:4])

            crop = safe_crop(frame, x1, y1, x2, y2)
            if crop is None:
                continue

            # OCR
            plate = ocr_plate(crop)

            if plate == "unknown":
                continue

            confirmed = tracker.add(plate)

            if confirmed:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")

                full_path = os.path.join(
                    FULL_CROP_PATH,
                    f"{confirmed}_{ts}.jpg"
                )

                min_path = os.path.join(
                    MIN_CROP_PATH,
                    f"{confirmed}_{ts}.jpg"
                )

                cv2.imwrite(full_path, frame)
                cv2.imwrite(min_path, crop)

                print(f"✅ PLATE OK: {confirmed}")

                return full_path, min_path, confirmed

    print("⚠ LPR TIMEOUT")
    return None, None, None


# ===============================
# TEST
# ===============================
if __name__ == "__main__":
    f, m, p = scan_plate()
    print("FULL :", f)
    print("MIN  :", m)
    print("PLATE:", p)