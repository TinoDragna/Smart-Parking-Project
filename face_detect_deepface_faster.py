import cv2
import numpy as np
from deepface import DeepFace
import os
from datetime import datetime
import threading
import time

# Tạo thư mục database
if not os.path.exists("database"):
    os.makedirs("database")
    print("Đã tạo thư mục 'database'")

# Cấu hình tối ưu
MODEL_NAME = "Facenet"  # Facenet nhanh hơn VGG-Face
DETECTOR_BACKEND = "opencv"  # opencv nhanh nhất
DISTANCE_METRIC = "cosine"
THRESHOLD = 0.5

# Khởi động webcam
video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Giảm resolution
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Biến global
detected_faces = []
face_to_add = None
processing = False
frame_to_process = None
process_count = 0

print("=" * 50)
print("HƯỚNG DẪN:")
print("- Webcam tự động phát hiện khuôn mặt")
print("- Nhấn 'a' để thêm khuôn mặt Unknown vào database")
print("- Nhấn 'q' để thoát")
print("=" * 50)

# Cache database embeddings để tăng tốc
database_embeddings = {}
database_last_update = 0

def load_database_embeddings():
    """Load tất cả embeddings từ database vào RAM"""
    global database_embeddings, database_last_update
    
    current_time = time.time()
    # Chỉ reload mỗi 5 giây
    if current_time - database_last_update < 5:
        return
    
    database_embeddings = {}
    if not os.path.exists("database"):
        return
    
    for filename in os.listdir("database"):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join("database", filename)
            try:
                embedding_objs = DeepFace.represent(
                    img_path=filepath,
                    model_name=MODEL_NAME,
                    detector_backend=DETECTOR_BACKEND,
                    enforce_detection=False
                )
                if embedding_objs:
                    name = os.path.splitext(filename)[0]
                    # Bỏ timestamp nếu có
                    name = '_'.join(name.split('_')[:-2]) if len(name.split('_')) > 2 else name
                    database_embeddings[name] = embedding_objs[0]["embedding"]
            except:
                pass
    
    database_last_update = current_time
    print(f"Đã load {len(database_embeddings)} khuôn mặt từ database")

def cosine_distance(embedding1, embedding2):
    """Tính khoảng cách cosine giữa 2 embeddings"""
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    return 1 - np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def find_matching_face_fast(face_embedding):
    """Tìm khuôn mặt khớp nhanh bằng cách so sánh embeddings đã cache"""
    if not database_embeddings:
        return None, None
    
    min_distance = float('inf')
    best_match = None
    
    for name, db_embedding in database_embeddings.items():
        distance = cosine_distance(face_embedding, db_embedding)
        if distance < min_distance:
            min_distance = distance
            best_match = name
    
    if min_distance < THRESHOLD:
        return best_match.replace('_', ' ').title(), min_distance
    return None, None

def process_frame_thread():
    """Thread xử lý frame riêng để không block UI"""
    global detected_faces, processing, frame_to_process, face_to_add
    
    while True:
        if frame_to_process is not None and not processing:
            processing = True
            frame = frame_to_process.copy()
            frame_to_process = None
            
            try:
                # Resize để xử lý nhanh hơn
                small_frame = cv2.resize(frame, (320, 240))
                
                # Detect faces với opencv (nhanh nhất)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                faces_detected = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                temp_faces = []
                
                for (x, y, w, h) in faces_detected:
                    # Scale tọa độ về kích thước gốc
                    x, y, w, h = x*2, y*2, w*2, h*2
                    
                    # Crop khuôn mặt
                    face_img = frame[y:y+h, x:x+w]
                    
                    if face_img.size > 0:
                        try:
                            # Lấy embedding
                            embedding_objs = DeepFace.represent(
                                img_path=face_img,
                                model_name=MODEL_NAME,
                                detector_backend="skip",  # Đã detect rồi
                                enforce_detection=False
                            )
                            
                            if embedding_objs:
                                embedding = embedding_objs[0]["embedding"]
                                name, distance = find_matching_face_fast(embedding)
                                
                                temp_faces.append({
                                    'box': (x, y, w, h),
                                    'name': name if name else 'Unknown',
                                    'distance': distance,
                                    'face_img': face_img,
                                    'embedding': embedding
                                })
                        except:
                            pass
                
                detected_faces = temp_faces
                if detected_faces and detected_faces[0]['name'] == 'Unknown':
                    face_to_add = detected_faces[0]['face_img']
                
            except Exception as e:
                pass
            
            processing = False
        
        time.sleep(0.01)

# Load database embeddings lần đầu
load_database_embeddings()

# Khởi động thread xử lý
processing_thread = threading.Thread(target=process_frame_thread, daemon=True)
processing_thread.start()

fps_time = time.time()
fps_counter = 0
fps_display = 0

while True:
    ret, frame = video_capture.read()
    
    if not ret:
        print("Không thể đọc frame từ webcam")
        break

    display_frame = frame.copy()
    
    # Gửi frame để xử lý (mỗi 3 frame)
    process_count += 1
    if process_count % 5 == 0 and not processing:
        frame_to_process = frame.copy()
    
    # Vẽ kết quả từ lần xử lý trước
    for idx, face in enumerate(detected_faces):
        x, y, w, h = face['box']
        name = face['name']
        distance = face['distance']
        
        # Màu
        color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
        
        # Vẽ khung
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
        
        # Label
        if distance is not None:
            label = f"{name} ({distance:.2f})"
        else:
            label = f"{name}"
        
        cv2.rectangle(display_frame, (x, y - 30), (x + w, y), color, cv2.FILLED)
        cv2.putText(display_frame, label, (x + 5, y - 8), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Tính FPS
    fps_counter += 1
    if time.time() - fps_time > 1:
        fps_display = fps_counter
        fps_counter = 0
        fps_time = time.time()
    
    # Hiển thị FPS và hướng dẫn
    cv2.putText(display_frame, f"FPS: {fps_display}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(display_frame, "Nhan 'a' de them | 'q' de thoat", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Hiển thị
    cv2.imshow('DeepFace Fast Recognition', display_frame)
    
    # Xử lý phím
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    
    elif key == ord('a') and face_to_add is not None:
        print("\n" + "=" * 50)
        print("Đã capture khuôn mặt!")
        name_input = input("Nhập tên (hoặc Enter để hủy): ").strip()
        
        if name_input:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name_input.replace(' ', '_')}_{timestamp}.jpg"
            filepath = os.path.join("database", filename)
            
            face_resized = cv2.resize(face_to_add, (224, 224))
            cv2.imwrite(filepath, face_resized)
            
            print(f"✓ Đã lưu: {filename}")
            
            # Reload database
            load_database_embeddings()
        else:
            print("Đã hủy")
        print("=" * 50 + "\n")
        
        face_to_add = None

video_capture.release()
cv2.destroyAllWindows()
print("\nĐã đóng webcam")