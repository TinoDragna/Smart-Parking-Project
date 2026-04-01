import cv2
import json
import numpy as np
import time
import os
from collections import defaultdict
from datetime import datetime

from detector import Detector
from utils import shrink_box

# ===============================
# 📌 CONFIG
# ===============================
SLOT_JSON = "bounding_boxes/bounding_boxes_5421.json"
OVERLAP_THRESHOLD = 0.25
CAR_CLASS_ID = 2
SLOT_CODE = ["A1", "B1", "C1"]

OUTPUT_PATH = "../../../smart_parking_data/slot_detection"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# ===============================
# 📌 Init detector
# ===============================
detector = Detector("yolo26m.pt", conf=0.15)


# ===============================
# 📌 Compute overlap
# ===============================
def compute_overlap(box, slot_pts, shape):
    x1, y1, x2, y2 = map(int, box)

    box_poly = np.array([
        [x1, y1], [x2, y1],
        [x2, y2], [x1, y2]
    ], dtype=np.int32)

    mask_slot = np.zeros(shape[:2], dtype=np.uint8)
    mask_box = np.zeros(shape[:2], dtype=np.uint8)

    cv2.fillPoly(mask_slot, [slot_pts], 1)
    cv2.fillPoly(mask_box, [box_poly], 1)

    intersection = np.logical_and(mask_slot, mask_box).sum()
    slot_area = mask_slot.sum()

    if slot_area == 0:
        return 0

    return intersection / slot_area


# ===============================
# 📌 Parking Tracker (like PlateTracker)
# ===============================
class ParkingTracker:
    def __init__(self, stable_interval=5, min_count=3):
        self.stable_interval = stable_interval
        self.min_count = min_count
        self.records = defaultdict(list)

    def _encode(self, result):
        # convert dict → string key
        return str(sorted(result.items()))

    def add(self, result):
        now = time.time()
        key = self._encode(result)

        self.records[key].append(now)

        # clean old records
        for k in list(self.records.keys()):
            self.records[k] = [
                t for t in self.records[k]
                if now - t <= self.stable_interval
            ]
            if not self.records[k]:
                del self.records[k]

        best_key = max(self.records, key=lambda k: len(self.records[k]))
        best_count = len(self.records[best_key])

        if best_count >= self.min_count:
            return eval(best_key)  # convert back to dict

        return None


# ===============================
# 📌 Core scan
# ===============================
def scan_parking(timeout=10):
    with open(SLOT_JSON, "r") as f:
        slots = json.load(f)

    tracker = ParkingTracker(stable_interval=5, min_count=3)
    start_time = time.time()

    print("📸 scan_parking: START")

    while time.time() - start_time < timeout:
        # ret, frame = camera.read()
        # if not ret:
        #     continue

        frame = cv2.imread("pics/IMG_5421.png")  # for testing with static image

        # 🔹 Detect
        boxes, clss, confs = detector.detect(frame)
        boxes = [shrink_box(b) for b in boxes]

        # 🔹 Map box → slots
        box_to_slots = []

        for box in boxes:
            overlapped = []

            for i, slot in enumerate(slots):
                pts = np.array(slot["points"], dtype=np.int32)

                overlap = compute_overlap(box, pts, frame.shape)

                if overlap > OVERLAP_THRESHOLD:
                    overlapped.append(i)

            box_to_slots.append(overlapped)

        # 🔹 Determine slot states
        slot_status = ["available"] * len(slots)

        violating_boxes_idx = set()

        for box_idx, overlapped in enumerate(box_to_slots):
            if len(overlapped) > 1:
                violating_boxes_idx.add(box_idx)

            cls = int(clss[box_idx])

            if cls != CAR_CLASS_ID:
                continue

            if len(overlapped) == 1:
                slot_status[overlapped[0]] = "occupied"

            elif len(overlapped) > 1:
                for s in overlapped:
                    slot_status[s] = "violation"

        # 🔹 Build result
        result = {
            "occupied": [],
            "available": [],
            "violations": []
        }

        for i, status in enumerate(slot_status):
            if status == "occupied":
                result["occupied"].append(SLOT_CODE[i])
            elif status == "available":
                result["available"].append(SLOT_CODE[i])
            else:
                result["violations"].append(SLOT_CODE[i])

        # 🔹 Stabilize (like PlateTracker)
        stable_result = tracker.add(result)

        if stable_result:
            for i, (box, cls, conf) in enumerate(zip(boxes, clss, confs)):
                x1, y1, x2, y2 = map(int, box)

                if int(cls) != CAR_CLASS_ID:
                    continue

                if i in violating_boxes_idx:
                    color = (0, 0, 255)  # 🔴 RED = violation
                    label = "VIOLATION"
                    thickness = 3
                else:
                    color = (255, 0, 0)  # 🔵 BLUE = normal car
                    label = "CAR"
                    thickness = 2

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            ts = datetime.now().strftime("%d%m%Y_%H%M%S")
            save_path = os.path.join(OUTPUT_PATH, f"parking_{ts}.jpg")

            cv2.imwrite(save_path, frame)

            print("✅ Parking stable")
            print("Saved frame:", save_path)
            print(stable_result)

            return save_path, stable_result

    print("⚠ Parking TIMEOUT")
    return None, None

if __name__ == "__main__":
    scan_parking()