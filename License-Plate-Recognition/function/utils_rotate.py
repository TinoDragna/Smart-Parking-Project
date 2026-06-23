import numpy as np
import math
import cv2

def changeContrast(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)
    limg = cv2.merge((cl,a,b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return result

def compute_skew(src_img, center_thres):
    if len(src_img.shape) == 3:
        h, w, _ = src_img.shape
    else:
        h, w = src_img.shape

    # Giảm nhiễu mượt hơn bằng GaussianBlur thay vì MedianBlur
    img = cv2.GaussianBlur(src_img, (3, 3), 0)
    edges = cv2.Canny(img, threshold1=50, threshold2=150, apertureSize=3, L2gradient=True)
    
    # Nới lỏng minLineLength từ w/1.5 xuống w/3 để bắt được các nét chữ hoặc đoạn viền ngắn khi xe bị chéo góc
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, minLineLength=w / 3.0, maxLineGap=h / 4.0)
    
    if lines is None:
        return 0.0

    angles = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            # Tính góc bằng độ (Degree) trực tiếp để dễ xử lý
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            
            # Chuẩn hóa góc về khoảng -45 đến 45 độ
            if ang > 45:
                ang -= 90
            elif ang < -45:
                ang += 90
                
            # Chỉ nhận các góc nghiêng nhẹ từ -20 đến 20 độ (biển số thực tế ít khi nghiêng hơn)
            if abs(ang) <= 20:
                angles.append(ang)

    if not angles:
        return 0.0

    # Lấy giá trị trung vị (Median) thay vì trung bình cộng để loại bỏ các góc nhiễu cực đoan
    return float(np.median(angles))

def deskew(src_img, change_cons, center_thres):
    # Khuyến khích bật change_cons=1 ở file main khi gọi hàm để tăng độ nét cho cạnh biển số
    if change_cons == 1:
        return rotate_image(src_img, compute_skew(changeContrast(src_img), center_thres))
    else:
        return rotate_image(src_img, compute_skew(src_img, center_thres))