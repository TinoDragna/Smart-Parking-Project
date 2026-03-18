
🚗 Smart Parking Project

Hệ thống Smart Parking sử dụng RFID kết hợp License Plate Recognition (LPR) và Face Recognition để kiểm soát xe ra/vào, quản lý bãi đỗ theo thời gian thực và tăng cường an ninh.

📦 Installation & Setup
1️⃣ Deploy source code
Copy toàn bộ thư mục smart-parking-project (branch develop)vào:
xampp/htdocs/

2️⃣ Start services
Mở XAMPP Control Panel
Start:
✅ Apache
✅ MySQL

3️⃣ Create database user
Truy cập phpMyAdmin:
http://localhost/phpmyadmin/index.php?route=/server/privileges&viewing_mode=server
Add user đúng với thông tin được cấu hình trong code (username, password).

4️⃣ Grant privileges
Cấp đầy đủ quyền cho user:
SELECT, INSERT, UPDATE, DELETE
CREATE, DROP, INDEX
Áp dụng cho database smart_parking

5️⃣ Load database & open web interface
Chạy file -----------------------

Truy cập hệ thống web:
http://localhost/Smart-Parking-Project/SmartParkingSystem/index.php

6️⃣ Start AI & Gate Service
Chạy script chính:
python subscribe_addLPR_Face.py


📌 Lưu ý
Có thể chỉnh trong plate_scanner.py để:
Test bằng camera
Hoặc test bằng ảnh tĩnh

🧪 Test Scenarios
🔹 Test 1: Xe 1 vào bãi (Slot A1)
RFID hợp lệ
LPR nhận diện biển số
Face Recognition xác thực
Gate mở
Slot A1 được chiếm

<br>
🔹 Test 2: Xe 2 vào bãi (Slot B1)
Quy trình tương tự
Slot B1 được chiếm

<br>
🔹 Test 3: Xem chi tiết bãi đỗ
Kiểm tra trạng thái slot
Xem RFID, biển số, thời gian vào

<br>
🔹 Test 4: Bãi FULL
❌ Không thể:
Check-out bằng thẻ chưa check-in
Check-in lại bằng thẻ đã ở trong bãi

<br>
🔹 Test 5: Xe ở A1 đi ra
RFID khác lúc vào → bị từ chối
RFID + License Plate + Face đúng → cho phép ra

Kết quả:
✅ Cập nhật database
✅ Lưu ảnh lúc exit
✅ Nhả slot A1

<br>
🔹 Test 6: Xe ở B1 đi ra
Face Recognition sai → không cho ra
Gate từ chối
Ghi log sự kiện

<br>
🔐 Security & Logging

Ảnh LPR và Face được:
📁 Lưu local
🔍 Dùng cho tra soát khi có sự cố
📊 Phục vụ security auditing
🤖 Có thể dùng để train / cải thiện model

Không dùng cho mục đích thương mại
📌 Notes

Hệ thống ở mức Prototype / Research
Chạy tốt trong môi trường Lab / Demo
Có thể mở rộng:
RBAC (phân quyền)
Dashboard realtime
Raspberry Pi / Edge deployment