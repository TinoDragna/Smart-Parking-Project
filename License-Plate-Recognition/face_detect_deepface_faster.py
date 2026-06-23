import cv2
import numpy as np
from deepface import DeepFace
import os
from datetime import datetime
import time
import urllib.request
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
THRESHOLD = 0.37
FACE_DB = "../smart_parking_data/face_img"

os.makedirs(FACE_DB, exist_ok=True)

# ===============================
# FIX 1: LOAD MODEL 1 LẦN DUY NHẤT
# ===============================
print("🔄 Loading DeepFace model...")
model = DeepFace.build_model(MODEL_NAME)
print("✅ Model loaded")

# =====================================================
# LOAD DNN FACE DETECTOR ONCE (ĐÃ ĐỔI LINK CHUẨN)
# =====================================================
proto_path = "deploy.prototxt"
model_path = "res10_300x300_ssd_iter_140000.caffemodel"

# Cấu hình Header giả lập trình duyệt để tránh bị GitHub chặn tải
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

if not os.path.exists(proto_path):
    print("📥 Downloading face detector configuration (deploy.prototxt)...")
    url_proto = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
    urllib.request.urlretrieve(url_proto, proto_path)

if not os.path.exists(model_path):
    print("📥 Downloading face detector weights (res10_300x300_ssd)...")
    # LINK ĐÃ SỬA CHUẨN ĐƯỜNG DẪN TRÊN GITHUB OPENCV
    url_model = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
    urllib.request.urlretrieve(url_model, model_path)

NET = cv2.dnn.readNetFromCaffe(proto_path, model_path)
print("✅ DNN Face Detector loaded")


# ===============================
# UTILS
# ===============================
def cosine_distance(e1, e2):
    e1 = np.array(e1)
    e2 = np.array(e2)
    return 1 - np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))


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


def get_best_face_dnn(frame, min_confidence=0.7):
    """Sử dụng Deep Learning SSD để tìm khuôn mặt chuẩn xác nhất, loại bỏ vật thể rác."""
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    NET.setInput(blob)
    detections = NET.forward()
    
    best_face = None
    max_area = 0
    
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > min_confidence:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            
            startX, startY = max(0, startX), max(0, startY)
            endX, endY = min(w - 1, endX), min(h - 1, endY)
            
            face_w = endX - startX
            face_h = endY - startY
            
            if face_w >= 100 and face_h >= 100:
                area = face_w * face_h
                if area > max_area:
                    max_area = area
                    best_face = (startX, startY, face_w, face_h)
                    
    return best_face


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

        face_box = get_best_face_dnn(frame, min_confidence=0.7)

        if face_box is None:
            detect_count = 0
            continue

        detect_count += 1
        if detect_count < 8:
            continue

        x, y, w, h = face_box
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

        face_box = get_best_face_dnn(frame, min_confidence=0.7)

        if face_box is None:
            detect_count = 0
            continue

        detect_count += 1
        if detect_count < 8:
            continue

        x, y, w, h = face_box
        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (224, 224))

        # ===== SAVE FILE =====
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        exit_path = os.path.join(FACE_DB, f"face_exit_{ts}.jpg")
        cv2.imwrite(exit_path, face)

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