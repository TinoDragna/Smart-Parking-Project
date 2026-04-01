import cv2
import json
import numpy as np
import time

from detector import Detector
from utils import shrink_box

# ===============================
# 📌 CONFIG
# ===============================
SLOT_JSON = "bounding_boxes/bounding_boxes_5421.json"
OVERLAP_THRESHOLD = 0.25
CAR_CLASS_ID = 2
SLOT_CODE = ["A1", "B1", "C1"]


# ===============================
# 📌 Init detector (load once)
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
# 📌 Core Parking Scan
# ===============================
def scan_parking(timeout=5):
    """
    Capture frames from camera and return parking state

    Returns:
        {
            "occupied": [...],
            "available": [...],
            "violations": [...]
        }
    """

    # 🔹 Load slots once
    with open(SLOT_JSON, "r") as f:
        slots = json.load(f)

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

        for box_idx, overlapped in enumerate(box_to_slots):
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
                result["occupied"].append(SLOT_CODE[i])  # map index to code
            elif status == "available":
                result["available"].append(SLOT_CODE[i])  # map index to code
            else:
                result["violations"].append(SLOT_CODE[i])  # map index to code

        print("✅ Parking scan complete")
        print(result)
        return result

    print("⚠ Parking scan TIMEOUT")
    return None

scan_parking()