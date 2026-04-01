import os
import cv2
import json
import numpy as np

from detector import Detector
from utils import shrink_box, classify_slot  # keep if you still want fallback

INPUT_FOLDER = "pics"
OUTPUT_FOLDER = "output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Init detector
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


for filename in os.listdir(INPUT_FOLDER):
    if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
        continue

    print(f"Processing {filename}...")

    # 🔹 Load slots
    slot_file_name = f"bounding_boxes_{filename.split('.')[0].split('_')[-1]}.json"
    slot_path = os.path.join("bounding_boxes", slot_file_name)

    if not os.path.exists(slot_path):
        print(f"Slot file {slot_file_name} not found. Skipping.")
        continue

    with open(slot_path, "r") as f:
        slots = json.load(f)

    path = os.path.join(INPUT_FOLDER, filename)
    image = cv2.imread(path)

    if image is None:
        print(f"Failed: {filename}")
        continue

    # 🔹 Detect
    boxes, clss, confs = detector.detect(image)

    # 🔹 Shrink boxes
    boxes = [shrink_box(b) for b in boxes]

    H, W = image.shape[:2]

    # 🔹 Map box → multiple slots (overlap-based)
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

        if cls != 2:  # not car → ignore or treat as violation
            continue

        if len(overlapped) == 1:
            # normal parking
            slot_status[overlapped[0]] = "car"

        elif len(overlapped) > 1:
            # violation: occupies multiple slots
            for s in overlapped:
                slot_status[s] = "violation"

    # 🔹 Draw detections
    for box, cls, conf in zip(boxes, clss, confs):
        x1, y1, x2, y2 = map(int, box)

        color = (0, 255, 0) if int(cls) == 2 else (0, 0, 255)
        label = f"{int(cls)} {conf:.2f}"

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 🔹 Draw slots
    for i, slot in enumerate(slots):
        pts = np.array(slot["points"], dtype=np.int32)
        pts = cv2.convexHull(pts)

        status = slot_status[i]

        if status == "available":
            color = (0, 255, 0) #green
        elif status == "car":
            color = (255, 0, 0) #blue
        else:  # violation
            color = (0, 0, 255) #red

        cv2.polylines(image, [pts], True, color, 2)

        x, y = pts[0][0]
        cv2.putText(image, status, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 🔹 Save
    out_path = os.path.join(OUTPUT_FOLDER, filename)
    cv2.imwrite(out_path, image)

    print(f"Processed {filename}")

print("DONE")