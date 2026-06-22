import cv2
import numpy as np
from deepface import DeepFace
import os
from datetime import datetime
import time
from camera import entry_camera, exit_camera

# ===============================
# FIX 0: GIẢM CRASH (CỰC QUAN TRỌNG)
# ===============================
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# ===============================
# CONFIG
# ===============================
MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"
THRESHOLD = 0.4
FACE_DB = "../smart_parking_data/face_img"

os.makedirs(FACE_DB, exist_ok=True)

# ===============================
# FIX 1: LOAD MODEL 1 LẦN DUY NHẤT
# ===============================
print("🔄 Loading DeepFace model...")
model = DeepFace.build_model(MODEL_NAME)
print("✅ Model loaded")

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


# ===============================
# FIX 2: SAFE EMBEDDING FUNCTION
# ===============================
def get_embedding(img):
    try:
        rep = DeepFace.represent(
            img_path=img,
            model_name=MODEL_NAME,
            detector_backend="skip",
            enforce_detection=False
        )
        return rep[0]["embedding"]
    except Exception as e:
        print("⚠ EMBEDDING ERROR:", e)
        return None


# ===============================
# CHECK-IN FACE
# ===============================
def check_in_face(camera_obj, timeout=15):
    for _ in range(10):
        camera_obj.read()
        time.sleep(0.01)

    start = time.time()
    detect_count = 0

    while time.time() - start < timeout:
        ret, frame = camera_obj.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            detect_count = 0
            continue

        detect_count += 1
        if detect_count < 5:
            continue

        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        if w < 80 or h < 80:
            continue
        
        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (224, 224))

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
def check_out_face(face_entry_path, camera_obj, timeout=15):
    for _ in range(10):
        camera_obj.read()
        time.sleep(0.01)

    # ===== LOAD ENTRY EMBEDDING =====
    entry_emb = get_embedding(face_entry_path)
    if entry_emb is None:
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
        ret, frame = camera_obj.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            detect_count = 0
            continue

        detect_count += 1
        if detect_count < 5:
            continue

        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        if w < 80 or h < 80:
            continue
        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (224, 224))

        # ===== SAVE FILE =====
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        exit_path = os.path.join(FACE_DB, f"face_exit_{ts}.jpg")
        cv2.imwrite(exit_path, face)

        # ===== FIX 3: DÙNG FILE PATH (KHÔNG DÙNG numpy) =====
        exit_emb = get_embedding(exit_path)
        if exit_emb is None:
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