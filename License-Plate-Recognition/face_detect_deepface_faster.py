import cv2
import numpy as np
from deepface import DeepFace
import os
from datetime import datetime
import time
from camera import camera

# ===============================
# CONFIG
# ===============================
MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"
THRESHOLD = 0.145           # 🔥 An toàn, giảm false accept
FACE_DB = "database"

os.makedirs(FACE_DB, exist_ok=True)

# ===============================
# LOAD FACE CASCADE ONCE
# ===============================
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ===============================
# UTILS
# ===============================
def cosine_distance(e1, e2):
    e1 = np.array(e1)
    e2 = np.array(e2)
    return 1 - np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))


def extract_datetime_from_filename(filename):
    try:
        name = os.path.splitext(filename)[0]
        _, d, t = name.split("_")
        return f"{d[6:8]}/{d[4:6]}/{d[0:4]} {t[0:2]}:{t[2:4]}:{t[4:6]}"
    except:
        return None

# ===============================
# CHECK-IN FACE
# ===============================
def check_in_face(timeout=6):
    """
    ENTRY:
    - Detect mặt ổn định
    - Resize 224x224
    - Save ảnh
    """

    start = time.time()
    detect_count = 0

    while time.time() - start < timeout:
        ret, frame = camera.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 6)

        if len(faces) == 0:
            detect_count = 0
            continue

        detect_count += 1
        if detect_count < 3:
            continue

        x, y, w, h = faces[0]
        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (224, 224))   # 🔥 CHUẨN HOÁ

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(FACE_DB, f"face_{ts}.jpg")
        cv2.imwrite(path, face)

        return {
            "success": True,
            "image_path": path,
            "message": "Face saved"
        }

    return {
        "success": False,
        "image_path": None,
        "message": "Face timeout"
    }

# ===============================
# CHECK-OUT FACE
# ===============================
def check_out_face(face_entry_path, timeout=6):
    """
    EXIT:
    - LUÔN save ảnh EXIT
    - Resize giống ENTRY
    - CHỈ so với face ENTRY
    - Multi-frame → lấy dist nhỏ nhất
    """

    # LOAD ENTRY EMBEDDING
    try:
        entry_emb = DeepFace.represent(
            img_path=face_entry_path,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=False
        )[0]["embedding"]
    except:
        return {
            "success": False,
            "image_path": None,
            "message": "Entry face invalid"
        }

    start = time.time()
    detect_count = 0
    best_dist = 1.0
    best_exit_path = None

    while time.time() - start < timeout:
        ret, frame = camera.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 6)

        if len(faces) == 0:
            detect_count = 0
            continue

        detect_count += 1
        if detect_count < 3:
            continue

        x, y, w, h = faces[0]
        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (224, 224))   # 🔥 CHUẨN HOÁ

        # SAVE EXIT IMAGE (ALWAYS)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        exit_path = os.path.join(FACE_DB, f"face_exit_{ts}.jpg")
        cv2.imwrite(exit_path, face)

        try:
            exit_emb = DeepFace.represent(
                img_path=face,
                model_name=MODEL_NAME,
                detector_backend="skip",
                enforce_detection=False
            )[0]["embedding"]
        except:
            continue

        dist = cosine_distance(exit_emb, entry_emb)

        if dist < best_dist:
            best_dist = dist
            best_exit_path = exit_path

        if best_dist < THRESHOLD:
            break

    if best_exit_path is None:
        return {
            "success": False,
            "image_path": None,
            "message": "No face captured"
        }

    if best_dist < THRESHOLD:
        return {
            "success": True,
            "image_path": best_exit_path,
            "confidence": round(1 - best_dist, 3),
            "message": "Face verified"
        }

    return {
        "success": False,
        "image_path": best_exit_path,
        "confidence": round(1 - best_dist, 3),
        "message": "Face mismatch"
    }
