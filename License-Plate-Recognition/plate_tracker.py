import time
from collections import defaultdict

class PlateTracker:
    def __init__(self, stable_interval=20, clear_interval=600, min_count=3):    #gia tri mac dinh ban dau
        """
        stable_interval: khoảng thời gian (s) để tính biển ổn định, ví dụ 20s
        clear_interval: thời gian (s) để xóa biển cũ khỏi bộ nhớ, ví dụ 600s (10 phút)
        min_count: số lần OCR trùng để xác nhận lưu
        """
        self.stable_interval = stable_interval
        self.clear_interval = clear_interval
        self.min_count = min_count
        self.plate_records = defaultdict(list)  # {plate: [timestamps]}
        self.saved_plates = {}  # {plate: last_saved_time}

    def add_plate(self, plate_text):
        now = time.time()
        self.plate_records[plate_text].append(now)

        # Xóa OCR quá cũ
        for p in list(self.plate_records.keys()):
            self.plate_records[p] = [t for t in self.plate_records[p] if now - t <= self.stable_interval]
            if not self.plate_records[p]:
                del self.plate_records[p]

        # Biển OCR ổn định nhất
        if self.plate_records:
            best_plate = max(self.plate_records, key=lambda k: len(self.plate_records[k]))
            best_count = len(self.plate_records[best_plate])

            if best_count >= self.min_count and best_plate not in self.saved_plates:
                self.saved_plates[best_plate] = now
                print(f"✅ [LOCAL] Saved stable plate: {best_plate}")
                return best_plate
        return None

    def cleanup_saved(self):
        now = time.time()
        expired = [plate for plate, t in self.saved_plates.items() if now - t > self.clear_interval]
        for plate in expired:
            print(f"🧹 [CLEANUP] Removed expired plate: {plate}")
            del self.saved_plates[plate]

    def get_saved_plates(self):
        """Trả về danh sách biển đã lưu (dành cho upDatabase dùng để upload lên DB thật)"""
        self.cleanup_saved()
        return list(self.saved_plates.keys())
