from ultralytics import YOLO

class Detector:
    def __init__(self, model_path, conf=0.25):
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, image):
        results = self.model(image, conf=self.conf, verbose=False)[0]

        boxes = []
        clss = []
        confs = []

        if results.boxes is None:
            return boxes, clss, confs

        for b in results.boxes:
            x1, y1, x2, y2 = b.xyxy[0].tolist()
            cls = int(b.cls[0].item())
            conf = float(b.conf[0].item())

            boxes.append([x1, y1, x2, y2])
            clss.append(cls)
            confs.append(conf)

        return boxes, clss, confs