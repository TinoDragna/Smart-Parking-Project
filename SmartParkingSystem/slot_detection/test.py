import cv2
from ultralytics import solutions

im0 = cv2.imread("pics/IMG_5421.png")

# Initialize parking management object
parkingmanager = solutions.ParkingManagement(
    model="yolo26m.pt",
    json_file="bounding_boxes/bounding_boxes_5421.json",
    conf=0.15,
)

# Process the image
results = parkingmanager.process(im0)

# Save or display the result
cv2.imwrite("parking_result.png", results.plot_im)  # save

print(f"Occupied spaces: {parkingmanager.pr_info['Occupancy']}")
print(f"Available spaces: {parkingmanager.pr_info['Available']}")
 