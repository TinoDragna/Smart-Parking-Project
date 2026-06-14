# import cv2

# cam = cv2.VideoCapture(1)
# print("Opened:", cam.isOpened())

# ret, frame = cam.read()
# print("Read:", ret)

# cam.release()

import cv2

cap = cv2.VideoCapture(
    "https://iot.eiu.com.vn/pi5Picam/stream.mjpg"
)

print(cap.isOpened())
