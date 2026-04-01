import cv2
import time
from ultralytics import solutions

# Stream source (RTSP / webcam / URL)
stream_url = "rtsp://your_stream_here"
cap = cv2.VideoCapture(stream_url)

assert cap.isOpened(), "Error opening stream"

# Init model
parkingmanager = solutions.ParkingManagement(
    model="yolo26m.pt",
    json_file="bounding_boxes/bounding_boxes_5421.json",
    conf=0.15,
)

# Video writer (optional, if you want output video)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 25  # fallback

out = cv2.VideoWriter(
    "parking_result.avi",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (w, h)
)

# Capture only 5 seconds
start_time = time.time()
duration = 5

last_result = None  # store last processed frame

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Stop after 5 seconds
    if time.time() - start_time > duration:
        break

    results = parkingmanager.process(frame)
    last_result = results.plot_im

    out.write(last_result)

# Save final frame as image (like your original code)
if last_result is not None:
    cv2.imwrite("parking_result.png", last_result)

cap.release()
out.release()
cv2.destroyAllWindows()

# Print stats
print(f"Occupied spaces: {parkingmanager.pr_info['Occupancy']}")
print(f"Available spaces: {parkingmanager.pr_info['Available']}")