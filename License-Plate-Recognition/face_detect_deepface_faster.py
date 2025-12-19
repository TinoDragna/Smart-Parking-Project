import cv2
import numpy as np
from deepface import DeepFace
import os
from datetime import datetime
import time

# ===============================
# CONFIG
# ===============================
MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"
THRESHOLD = 0.4
FACE_DB = "database"

os.makedirs(FACE_DB, exist_ok=True)

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
    Chụp 1 khuôn mặt rõ → lưu → trả path
    Dùng cho ENTRY
    """
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return {"success": False, "image_path": None, "message": "Camera error"}

    start = time.time()
    detect_count = 0

    while time.time() - start < timeout:
        ret, frame = cam.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        ).detectMultiScale(gray, 1.1, 6)

        if len(faces) == 0:
            detect_count = 0
            continue

        detect_count += 1
        if detect_count < 3:
            continue

        x, y, w, h = faces[0]
        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (224, 224))

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"face_{ts}.jpg"
        path = os.path.join(FACE_DB, fname)
        cv2.imwrite(path, face)

        cam.release()
        return {
            "success": True,
            "image_path": path,
            "message": f"Face saved at {extract_datetime_from_filename(fname)}"
        }

    cam.release()
    return {"success": False, "image_path": None, "message": "Face timeout"}

# ===============================
# CHECK-OUT FACE
# ===============================
def check_out_face(timeout=6):
    """
    So khớp khuôn mặt hiện tại với DB
    Dùng cho EXIT
    """

    # Load embeddings DB
    db_embeddings = {}
    for f in os.listdir(FACE_DB):
        if f.endswith(".jpg"):
            try:
                emb = DeepFace.represent(
                    img_path=os.path.join(FACE_DB, f),
                    model_name=MODEL_NAME,
                    detector_backend=DETECTOR_BACKEND,
                    enforce_detection=False
                )[0]["embedding"]
                db_embeddings[f] = emb
            except:
                pass

    if not db_embeddings:
        return {"success": False, "image_path": None, "message": "Empty face DB"}

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return {"success": False, "image_path": None, "message": "Camera error"}

    start = time.time()
    detect_count = 0

    while time.time() - start < timeout:
        ret, frame = cam.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        ).detectMultiScale(gray, 1.1, 6)

        if len(faces) == 0:
            detect_count = 0
            continue

        detect_count += 1
        if detect_count < 3:
            continue

        x, y, w, h = faces[0]
        face = frame[y:y+h, x:x+w]

        try:
            emb = DeepFace.represent(
                img_path=face,
                model_name=MODEL_NAME,
                detector_backend="skip",
                enforce_detection=False
            )[0]["embedding"]
        except:
            continue

        best, best_d = None, 1.0
        for fn, db_emb in db_embeddings.items():
            d = cosine_distance(emb, db_emb)
            if d < best_d:
                best, best_d = fn, d

        if best and best_d < THRESHOLD:
            cam.release()
            return {
                "success": True,
                "image_path": os.path.join(FACE_DB, best),
                "confidence": 1 - best_d,
                "datetime": extract_datetime_from_filename(best),
                "message": "Face verified"
            }

        cam.release()
        return {"success": False, "image_path": None, "message": "Face mismatch"}

    cam.release()
    return {"success": False, "image_path": None, "message": "Face timeout"}
