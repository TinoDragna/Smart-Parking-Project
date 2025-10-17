from flask import Flask, Response, render_template
import cv2
import time

import torch_patch

import torch
import function.utils_rotate as utils_rotate
import function.helper as helper

app = Flask(__name__)

# Mở webcam
vid = cv2.VideoCapture(0)

# Load mô hình YOLOv5
yolo_LP_detect = torch.hub.load(
    'yolov5', 'custom',
    path='model/LP_detector_nano_61.pt',
    force_reload=True,
    source='local'
)

yolo_license_plate = torch.hub.load(
    'yolov5', 'custom',
    path='model/LP_ocr_nano_62.pt',
    force_reload=True,
    source='local'
)
yolo_license_plate.conf = 0.60

prev_frame_time = 0

def generate_frames():
    global prev_frame_time
    while True:
        ret, frame = vid.read()
        if not ret:
            continue

        # ------------------ Xử lý AI ------------------
        plates = yolo_LP_detect(frame, size=640)
        list_plates = plates.pandas().xyxy[0].values.tolist()
        list_read_plates = set()

        for plate in list_plates:
            flag = 0
            x = int(plate[0])
            y = int(plate[1])
            w = int(plate[2] - plate[0])
            h = int(plate[3] - plate[1])
            crop_img = frame[y:y+h, x:x+w]

            # Vẽ bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,225), 2)

            # OCR biển số
            lp = ""
            for cc in range(0,2):
                for ct in range(0,2):
                    lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                    if lp != "unknown":
                        list_read_plates.add(lp)
                        cv2.putText(frame, lp, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                        flag = 1
                        break
                if flag == 1:
                    break

        # FPS
        new_frame_time = time.time()
        fps = int(1/(new_frame_time - prev_frame_time + 1e-5))
        prev_frame_time = new_frame_time
        cv2.putText(frame, f'FPS: {fps}', (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100,255,0), 2)
        # ------------------ Kết thúc AI ------------------

        # Encode sang JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')  # HTML dùng Bootstrap hiển thị

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
