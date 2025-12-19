import cv2
import numpy as np
from deepface import DeepFace
import os
from datetime import datetime
import threading
import time

# Cấu hình global
MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"
DISTANCE_METRIC = "cosine"
THRESHOLD = 0.4

def get_database_path():
    """Trả về đường dẫn thư mục database"""
    return os.path.abspath("database")

def get_image_path(filename):
    """Trả về đường dẫn đầy đủ của một ảnh trong database"""
    return os.path.abspath(os.path.join("database", filename))

def extract_datetime_from_filename(filename):
    """Trích xuất ngày giờ từ tên file"""
    try:
        basename = os.path.splitext(filename)[0]
        parts = basename.split('_')
        
        if len(parts) >= 3 and parts[0] == 'face':
            date_str = parts[1]
            time_str = parts[2]
            
            if len(date_str) == 8 and len(time_str) == 6:
                year = date_str[0:4]
                month = date_str[4:6]
                day = date_str[6:8]
                hour = time_str[0:2]
                minute = time_str[2:4]
                second = time_str[4:6]
                
                return f"{day}/{month}/{year} {hour}:{minute}:{second}"
    except Exception as e:
        print(f"Lỗi parse datetime từ {filename}: {e}")
    
    return None

def cosine_distance(embedding1, embedding2):
    """Tính khoảng cách cosine giữa 2 embeddings"""
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    return 1 - np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))


def check_in_face():
    """
    CHECK-IN: Chụp và lưu khuôn mặt mới khi vào
    Returns:
        str: Đường dẫn tuyệt đối của ảnh đã lưu, hoặc None nếu thất bại
    """
    
    # Tạo thư mục database
    if not os.path.exists("database"):
        os.makedirs("database")

    # Khởi động webcam
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    class SharedState:
        detected_faces = []
        processing = False
        frame_to_process = None
        process_count = 0
        face_detected_count = 0
        saved_image_path = None
        should_exit = False

    state = SharedState()

    print("\n" + "=" * 60)
    print("CHẾ ĐỘ CHECK-IN (VÀO)")
    print("- Đang chụp khuôn mặt để lưu vào hệ thống...")
    print("- Nhấn 'q' để hủy")
    print("=" * 60)

    def process_frame_thread():
        """Thread xử lý frame"""
        while True:
            if state.should_exit:
                break
                
            if state.frame_to_process is not None and not state.processing:
                state.processing = True
                frame = state.frame_to_process.copy()
                state.frame_to_process = None
                
                try:
                    small_frame = cv2.resize(frame, (320, 240))
                    
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                    faces_detected = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))
                    
                    temp_faces = []
                    
                    if len(faces_detected) > 0:
                        state.face_detected_count += 1
                        
                        faces_detected = sorted(faces_detected, key=lambda f: f[2]*f[3], reverse=True)
                        x, y, w, h = faces_detected[0]
                        x, y, w, h = x*2, y*2, w*2, h*2
                        
                        face_img = frame[y:y+h, x:x+w]
                        
                        if face_img.size > 0:
                            temp_faces.append({
                                'box': (x, y, w, h),
                                'label': 'Detecting...',
                                'face_img': face_img
                            })
                            
                            # Chụp sau khi detect ổn định 3 frames
                            if state.face_detected_count >= 3:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"face_{timestamp}.jpg"
                                filepath = os.path.join("database", filename)
                                
                                face_resized = cv2.resize(face_img, (224, 224))
                                cv2.imwrite(filepath, face_resized)
                                
                                state.saved_image_path = get_image_path(filename)
                                
                                print("\n" + "=" * 50)
                                print(f"✓ CHECK-IN THÀNH CÔNG!")
                                print(f"✓ Tên file: {filename}")
                                print(f"✓ Đường dẫn: {state.saved_image_path}")
                                print(f"✓ Thời gian: {extract_datetime_from_filename(filename)}")
                                print("=" * 50 + "\n")
                                
                                state.should_exit = True
                    else:
                        state.face_detected_count = 0
                    
                    state.detected_faces = temp_faces
                    
                except Exception as e:
                    pass
                
                state.processing = False
            
            time.sleep(0.01)

    processing_thread = threading.Thread(target=process_frame_thread, daemon=True)
    processing_thread.start()

    fps_time = time.time()
    fps_counter = 0
    fps_display = 0

    while True:
        if state.should_exit:
            break
            
        ret, frame = video_capture.read()
        
        if not ret:
            print("Không thể đọc frame từ webcam")
            break

        display_frame = frame.copy()
        
        state.process_count += 1
        if state.process_count % 3 == 0 and not state.processing:
            state.frame_to_process = frame.copy()
        
        for face in state.detected_faces:
            x, y, w, h = face['box']
            label = face['label']
            
            color = (0, 255, 255)  # Màu vàng cho check-in
            
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
            cv2.rectangle(display_frame, (x, y - 30), (x + 200, y), color, cv2.FILLED)
            cv2.putText(display_frame, label, (x + 5, y - 8), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        fps_counter += 1
        if time.time() - fps_time > 1:
            fps_display = fps_counter
            fps_counter = 0
            fps_time = time.time()
        
        cv2.putText(display_frame, f"FPS: {fps_display}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(display_frame, "CHECK-IN MODE | 'q' de huy", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow('Face Recognition - CHECK-IN', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    
    return state.saved_image_path


def check_out_face():
    """
    CHECK-OUT: Xác minh khuôn mặt với database khi ra
    Returns:
        dict: {
            'success': bool,           # True nếu nhận diện thành công
            'image_path': str,         # Đường dẫn ảnh trong database
            'datetime': str,           # Ngày giờ check-in
            'confidence': float,       # Độ tin cậy (0-1)
            'message': str            # Thông báo
        }
    """
    
    if not os.path.exists("database"):
        return {
            'success': False,
            'image_path': None,
            'datetime': None,
            'confidence': 0.0,
            'message': 'Database trống, không có dữ liệu để so sánh'
        }

    # Load database embeddings
    database_embeddings = {}
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
                    database_embeddings[filename] = embedding_objs[0]["embedding"]
            except:
                pass
    
    print(f"Đã load {len(database_embeddings)} khuôn mặt từ database")

    # Khởi động webcam
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    class SharedState:
        detected_faces = []
        processing = False
        frame_to_process = None
        process_count = 0
        face_detected_count = 0
        result = None
        should_exit = False

    state = SharedState()

    print("\n" + "=" * 60)
    print("CHẾ ĐỘ CHECK-OUT (RA)")
    print("- Đang xác minh khuôn mặt với dữ liệu đã lưu...")
    print("- Nhấn 'q' để hủy")
    print("=" * 60)

    def find_matching_face(face_embedding):
        """Tìm khuôn mặt khớp trong database"""
        if not database_embeddings:
            return None, None, None
        
        min_distance = float('inf')
        best_match_filename = None
        
        for filename, db_embedding in database_embeddings.items():
            distance = cosine_distance(face_embedding, db_embedding)
            if distance < min_distance:
                min_distance = distance
                best_match_filename = filename
        
        if min_distance < THRESHOLD:
            datetime_str = extract_datetime_from_filename(best_match_filename)
            confidence = 1 - min_distance
            return best_match_filename, datetime_str, confidence
        return None, None, None

    def process_frame_thread():
        """Thread xử lý frame"""
        while True:
            if state.should_exit:
                break
                
            if state.frame_to_process is not None and not state.processing:
                state.processing = True
                frame = state.frame_to_process.copy()
                state.frame_to_process = None
                
                try:
                    small_frame = cv2.resize(frame, (320, 240))
                    
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                    faces_detected = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))
                    
                    temp_faces = []
                    
                    if len(faces_detected) > 0:
                        state.face_detected_count += 1
                        
                        faces_detected = sorted(faces_detected, key=lambda f: f[2]*f[3], reverse=True)
                        x, y, w, h = faces_detected[0]
                        x, y, w, h = x*2, y*2, w*2, h*2
                        
                        face_img = frame[y:y+h, x:x+w]
                        
                        if face_img.size > 0 and state.face_detected_count >= 3:
                            try:
                                embedding_objs = DeepFace.represent(
                                    img_path=face_img,
                                    model_name=MODEL_NAME,
                                    detector_backend="skip",
                                    enforce_detection=False
                                )
                                
                                if embedding_objs:
                                    embedding = embedding_objs[0]["embedding"]
                                    filename, datetime_str, confidence = find_matching_face(embedding)
                                    
                                    if filename:
                                        # Tìm thấy!
                                        image_path = get_image_path(filename)
                                        
                                        temp_faces.append({
                                            'box': (x, y, w, h),
                                            'label': f"VERIFIED: {datetime_str}",
                                            'confidence': confidence
                                        })
                                        
                                        state.result = {
                                            'success': True,
                                            'image_path': image_path,
                                            'datetime': datetime_str,
                                            'confidence': confidence,
                                            'message': f'Xác minh thành công! Check-in lúc {datetime_str}'
                                        }
                                        
                                        print("\n" + "=" * 50)
                                        print(f"✓ CHECK-OUT THÀNH CÔNG!")
                                        print(f"✓ Check-in lúc: {datetime_str}")
                                        print(f"✓ Đường dẫn ảnh: {image_path}")
                                        print(f"✓ Độ tin cậy: {confidence:.2%}")
                                        print("=" * 50 + "\n")
                                        
                                        state.should_exit = True
                                    else:
                                        # Không tìm thấy
                                        temp_faces.append({
                                            'box': (x, y, w, h),
                                            'label': "UNKNOWN - Not in database",
                                            'confidence': 0
                                        })
                                        
                                        state.result = {
                                            'success': False,
                                            'image_path': None,
                                            'datetime': None,
                                            'confidence': 0.0,
                                            'message': 'Không tìm thấy khuôn mặt trong database'
                                        }
                                        
                                        print("\n" + "=" * 50)
                                        print(f"❌ CHECK-OUT THẤT BẠI!")
                                        print(f"❌ Khuôn mặt không có trong hệ thống")
                                        print("=" * 50 + "\n")
                                        
                                        state.should_exit = True
                            except:
                                pass
                    else:
                        state.face_detected_count = 0
                    
                    state.detected_faces = temp_faces
                    
                except Exception as e:
                    pass
                
                state.processing = False
            
            time.sleep(0.01)

    processing_thread = threading.Thread(target=process_frame_thread, daemon=True)
    processing_thread.start()

    fps_time = time.time()
    fps_counter = 0
    fps_display = 0

    while True:
        if state.should_exit:
            break
            
        ret, frame = video_capture.read()
        
        if not ret:
            print("Không thể đọc frame từ webcam")
            break

        display_frame = frame.copy()
        
        state.process_count += 1
        if state.process_count % 3 == 0 and not state.processing:
            state.frame_to_process = frame.copy()
        
        for face in state.detected_faces:
            x, y, w, h = face['box']
            label = face['label']
            confidence = face.get('confidence', 0)
            
            if "VERIFIED" in label:
                color = (0, 255, 0)  # Xanh lá - Thành công
            elif "UNKNOWN" in label:
                color = (0, 0, 255)  # Đỏ - Thất bại
            else:
                color = (255, 255, 0)  # Vàng - Đang xử lý
            
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
            
            # Vẽ label
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(display_frame, (x, y - 30), (x + text_width + 10, y), color, cv2.FILLED)
            cv2.putText(display_frame, label, (x + 5, y - 8), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Hiển thị confidence nếu có
            if confidence > 0:
                conf_text = f"Confidence: {confidence:.1%}"
                cv2.putText(display_frame, conf_text, (x + 5, y + h + 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        fps_counter += 1
        if time.time() - fps_time > 1:
            fps_display = fps_counter
            fps_counter = 0
            fps_time = time.time()
        
        cv2.putText(display_frame, f"FPS: {fps_display}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(display_frame, "CHECK-OUT MODE | 'q' de huy", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow('Face Recognition - CHECK-OUT', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            state.result = {
                'success': False,
                'image_path': None,
                'datetime': None,
                'confidence': 0.0,
                'message': 'Người dùng hủy thao tác'
            }
            break

    video_capture.release()
    cv2.destroyAllWindows()
    
    return state.result


# ==================== EXAMPLE USAGE ====================
if __name__ == "__main__":
    # Test check-in
    print("Testing CHECK-IN...")
    image_path = check_in_face()
    print(f"Result: {image_path}")
    
    # Test check-out
    print("\nTesting CHECK-OUT...")
    result = check_out_face()
    print(f"Result: {result}")