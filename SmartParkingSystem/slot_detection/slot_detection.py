import cv2
import json
import numpy as np

from detector import Detector
from utils import shrink_box

# Init detector (keep global or move outside if reused)
detector = Detector("yolo26m.pt", conf=0.15)


# 🔹 Compute overlap between box and polygon slot
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


# 🔹 MAIN FUNCTION
def process_image(image_path, slot_json_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Failed to load image")

    with open(slot_json_path, "r") as f:
        slots = json.load(f)

    # 🔹 Detect
    boxes, clss, confs = detector.detect(image)

    # 🔹 Shrink boxes
    boxes = [shrink_box(b) for b in boxes]

    # 🔹 Overlap mapping
    overlap_threshold = 0.25
    box_to_slots = []

    for box in boxes:
        overlapped = []

        for i, slot in enumerate(slots):
            pts = np.array(slot["points"], dtype=np.int32)
            overlap = compute_overlap(box, pts, image.shape)

            if overlap > overlap_threshold:
                overlapped.append(i)

        box_to_slots.append(overlapped)

    # 🔹 Determine slot states
    slot_status = ["available"] * len(slots)

    for box_idx, overlapped in enumerate(box_to_slots):
        cls = int(clss[box_idx])

        if cls != 2:
            continue

        if len(overlapped) == 1:
            slot_status[overlapped[0]] = "occupied"

        elif len(overlapped) > 1:
            for s in overlapped:
                slot_status[s] = "violation"

    # 🔹 Convert to structured output
    result = {
        "occupied": [],
        "available": [],
        "violations": []
    }

    for i, status in enumerate(slot_status):
        if status == "occupied":
            result["occupied"].append(i)
        elif status == "available":
            result["available"].append(i)
        else:
            result["violations"].append(i)

    return result