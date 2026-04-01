import cv2
import os
from ultralytics import YOLO

model = YOLO("yolo26m.pt")

input_folder = "pics"
output_folder = "output_yolo"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".png", ".jpeg")):
        path = os.path.join(input_folder, filename)

        im0 = cv2.imread(path)
        if im0 is None:
            print(f"Failed to load {filename}")
            continue

        results = model(im0, conf=0.15)

        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            clss = results[0].boxes.cls.cpu().numpy()
            confs = results[0].boxes.conf.cpu().numpy()

            for box, cls, conf in zip(boxes, clss, confs):
                x1, y1, x2, y2 = map(int, box)

                # color: green = car, red = others
                if int(cls) == 2:
                    color = (0, 255, 0)
                    label_name = "car"
                else:
                    color = (0, 0, 255)
                    label_name = f"cls_{int(cls)}"

                label = f"{label_name} {conf:.2f}"

                cv2.rectangle(im0, (x1, y1), (x2, y2), color, 2)
                cv2.putText(im0, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 3,
                            color, 7)

        # save output
        out_path = os.path.join(output_folder, filename)
        cv2.imwrite(out_path, im0)

        print(f"Processed {filename}")

print("DONE.")