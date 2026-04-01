import numpy as np
from shapely.geometry import Polygon, box as shapely_box

# 🔹 Compute overlap ratio (slot-based)
def compute_overlap(slot_points, bbox):
    slot_poly = Polygon(slot_points)
    bbox_poly = shapely_box(*bbox)

    if not slot_poly.is_valid:
        return 0

    inter_area = slot_poly.intersection(bbox_poly).area
    slot_area = slot_poly.area

    if slot_area == 0:
        return 0

    return inter_area / slot_area


# 🔹 Shrink box (reduce noise)
def shrink_box(bbox, factor=0.8):
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    w = (x2 - x1) * factor
    h = (y2 - y1) * factor

    return [
        cx - w / 2,
        cy - h / 2,
        cx + w / 2,
        cy + h / 2
    ]


# 🔹 Assign each box → BEST slot (IMPORTANT)
def assign_boxes_to_slots(slots, boxes):
    assignment = [-1] * len(boxes)

    for i, box in enumerate(boxes):
        best_slot = -1
        best_overlap = 0

        for j, slot in enumerate(slots):
            overlap = compute_overlap(slot["points"], box)

            if overlap > best_overlap:
                best_overlap = overlap
                best_slot = j

        if best_overlap > 0.15:
            assignment[i] = best_slot

    return assignment


# 🔹 Final slot classification
def classify_slot(slot_idx, slots, boxes, clss, assignment):
    overlaps = []
    classes = []

    for i, box in enumerate(boxes):
        if assignment[i] == slot_idx:
            overlap = compute_overlap(slots[slot_idx]["points"], box)
            overlaps.append(overlap)
            classes.append(clss[i])

    if not overlaps:
        return "available"

    best_idx = int(np.argmax(overlaps))
    best_cls = int(classes[best_idx])
    best_overlap = overlaps[best_idx]

    # 🚗 COCO class 2 = car
    if best_cls != 2:
        return "violation"

    # weak overlap → bad parking
    if best_overlap < 0.2:
        return "violation"

    # check if box assigned to multiple slots (should NOT happen now)
    if assignment.count(slot_idx) > 1:
        return "violation"

    return "car"