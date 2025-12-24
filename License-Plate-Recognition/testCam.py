import cv2

cam = cv2.VideoCapture(1)
print("Opened:", cam.isOpened())

ret, frame = cam.read()
print("Read:", ret)

cam.release()
