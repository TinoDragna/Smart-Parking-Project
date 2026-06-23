import cv2
import os
import time
# Import trực tiếp 2 instance camera bãi xe đã được định nghĩa sẵn trong camera.py
from camera import entry_camera, exit_camera 
# Import 2 hàm xử lý nhận diện khuôn mặt
from face_detect_deepface_faster import check_in_face, check_out_face

def run_test():
    print("🔄 Đang kiểm tra trạng thái kết nối 2 camera bãi xe...")
    print("⚠️  LƯU Ý: Đợi DeepFace nạp model (khoảng 30s - 1 phút), xin đừng ngắt tiến trình.")
    
    # Đợi các luồng chạy ngầm khởi tạo xong dữ liệu từ luồng Stream URL
    time.sleep(3)  

    # Kiểm tra luồng vào (Entry Camera)
    ret_entry, frame_entry = entry_camera.read()
    if not ret_entry or frame_entry is None:
        print("❌ LỖI: Không thể lấy tín hiệu từ ENTRY CAMERA (Cổng vào).")
        print("👉 Vui lòng kiểm tra lại thiết bị hoặc URL: http://172.16.10.28:8080/?action=stream")
        entry_camera.release()
        exit_camera.release()
        return

    # Kiểm tra luồng ra (Exit Camera)
    ret_exit, frame_exit = exit_camera.read()
    if not ret_exit or frame_exit is None:
        print("❌ LỖI: Không thể lấy tín hiệu từ EXIT CAMERA (Cổng ra).")
        print("👉 Vui lòng kiểm tra lại thiết bị hoặc URL: http://172.16.10.28:8000/stream.mjpg")
        entry_camera.release()
        exit_camera.release()
        return

    print("\n=======================================")
    print("🎉 KẾT NỐI THÀNH CÔNG CẢ 2 CAMERA BÃI XE")
    print("=======================================")
    
    try:
        # ---------------------------------------------
        # BƯỚC 1: QUÉT MẶT TẠI CỔNG VÀO (ENTRY CAMERA)
        # ---------------------------------------------
        print("\n🚗 [BƯỚC 1: XE VÀO - ĐANG QUÉT MẶT CHECK-IN]")
        print("-> Đang nhận diện khuôn mặt từ ENTRY CAMERA (Timeout: 15 giây)...")
        
        result_in = check_in_face(entry_camera, timeout=15)
        
        if not result_in["success"]:
            print(f"❌ Check-in THẤT BẠI: {result_in['message']}")
            print("Gợi ý: Kiểm tra xem góc camera vào có bị khuất, tối hoặc người lái xe đứng quá xa không.")
            return
            
        print(f"✅ Check-in THÀNH CÔNG!")
        print(f"📍 Ảnh cổng vào đã lưu tại: {result_in['image_path']}")
        
        # Mô phỏng thời gian xe di chuyển từ cổng vào đến cổng ra
        print("\n⏱ Giả lập xe đang di chuyển trong bãi (Chờ 5 giây)...")
        time.sleep(5)
        
        # ---------------------------------------------
        # BƯỚC 2: QUÉT MẶT TẠI CỔNG RA (EXIT CAMERA)
        # ---------------------------------------------
        print("\n🚙 [BƯỚC 2: XE RA - ĐANG QUÉT MẶT CHECK-OUT]")
        print("-> Đang nhận diện từ EXIT CAMERA và đối chiếu đối tượng...")
        
        face_entry_path = result_in["image_path"]
        result_out = check_out_face(face_entry_path, exit_camera, timeout=15)
        
        print("\n=======================================")
        print("📊 KẾT QUẢ ĐỐI CHIẾU CUỐI CÙNG GIỮA 2 CAMERA")
        print("=======================================")
        if result_out["success"]:
            print(f"🎉 XÁC THỰC THÀNH CÔNG! (Người lái xe trùng khớp - MỞ BARIE)")
            print(f"💬 Trạng thái: {result_out['message']}")
            print(f"📈 Độ trùng khớp: {result_out['confidence']} (Càng sát 1 càng khớp)")
            print(f"📍 Ảnh đối chứng lúc ra lưu tại: {result_out['image_path']}")
        else:
            print(f"❌ XÁC THỰC THẤT BẠI (CẢNH BÁO: KHÔNG TRÙNG KHỚP NGƯỜI): {result_out['message']}")
            if "confidence" in result_out:
                print(f"📉 Độ trùng khớp thực tế: {result_out['confidence']} (Yêu cầu hệ thống: > 0.6)")
            print(f"📍 Ảnh nghi vấn lúc ra lưu tại: {result_out['image_path']}")
            print("Gợi ý: Nếu báo 'Face mismatch', có thể xe bị đổi người lái lúc ra hoặc ánh sáng góc chụp 2 camera lệch nhau quá nhiều.")

    except Exception as e:
        print(f"❌ Lỗi hệ thống trong quá trình test: {e}")
        
    finally:
        # Giải phóng tài nguyên an toàn cho cả 2 camera chạy luồng ngầm
        print("\n🔄 Đang đóng luồng kết nối các camera ngầm...")
        entry_camera.release()
        exit_camera.release()
        cv2.destroyAllWindows()
        print("🔒 Hệ thống kiểm tra đóng an toàn.")

if __name__ == "__main__":
    run_test()