import faulthandler
faulthandler.enable()

import os
# Change the working directory to the directory where this script resides.
# This ensures that relative paths (like 'yolov5', 'model/...', '../smart_parking_data')
# resolve correctly even if the script is executed from a different directory.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import json
import time
import threading
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime
import re
from collections import deque
from flask import Flask, Response, jsonify
import requests
import logging


from plate_scanner import scan_plate
from face_detect_deepface_faster import check_in_face, check_out_face
from camera import entry_camera, exit_camera
from path_finder import find_path_by_slot

# O: Occupied, X: Empty
# 1: Occupied, 0: Empty
# =====================================================
# THREAD LOCKS & GLOBAL BUFFERS
# =====================================================
log_buffer = deque(maxlen=50)
log_lock = threading.Lock()     
state_lock = threading.Lock()   
db_lock = threading.Lock()      


def log(msg):
    log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(log_line, flush=True)
    with log_lock:
        log_buffer.append(log_line)


def norm_plate(p):
    if not p:
        return None
    return p.replace(" ", "").replace("-", "").upper()

# =====================================================
# DB CONNECTION WITH AUTO-RECONNECT
# =====================================================
_db_connection = None

def get_db_connection():
    global _db_connection
    with db_lock:
        if _db_connection is None:
            _db_connection = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="smart_parking",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        else:
            try:
                _db_connection.ping(reconnect=True)
            except Exception as e:
                log(f"⚠ DB Ping failed, reconnecting... Error: {e}")
                _db_connection = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="smart_parking",
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True
                )
        return _db_connection

db = get_db_connection()
log("✅ DB initialized and connected")

# =====================================================
# CRASH RECOVERY CACHE
# =====================================================
def save_cache(key, value_dict):
    try:
        conn = get_db_connection()
        json_str = json.dumps(value_dict)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO system_cache (cache_key, cache_value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE cache_value=%s
            """, (key, json_str, json_str))
    except Exception as e:
        log(f"⚠ Không thể lưu cache cho {key}: {e}")

def load_cache(key):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT cache_value FROM system_cache WHERE cache_key=%s LIMIT 1", (key,))
            row = cur.fetchone()
            if row:
                return json.loads(row['cache_value'])
    except Exception as e:
        log(f"⚠ Không thể tải cache cho {key}: {e}")
    return None

def clear_cache(key):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM system_cache WHERE cache_key=%s", (key,))
    except Exception as e:
        log(f"⚠ Không thể xóa cache {key}: {e}")

# =====================================================
# GATE LOG
# =====================================================
def write_log(gate, action, triggered_by):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO gatelog (GateType, Action, Time, TriggeredBy)
                VALUES (%s, %s, NOW(), %s)
            """, (gate, action, triggered_by))
        log(f"📝 GateLog | {gate} | {action} | {triggered_by}")
    except Exception as e:
        log(f"⚠ GateLog ERROR: {e}")

# =====================================================
# MQTT SETUP
# =====================================================
MQTT_SERVER = "172.16.2.4"
MQTT_PORT = 1883

client_id = "py_control_" + str(int(time.time()))
client = mqtt.Client(client_id=client_id)
client.connect(MQTT_SERVER, MQTT_PORT, 60)
log("✅ MQTT connected")

# =====================================================
# GLOBAL STATE
# =====================================================
irStatus = {"ENTRY": None, "EXIT": None}
slotStatus = {}  
pendingEntry = None   
START_SYSTEM_TIME = time.time()


# Xe đang chờ thanh toán và chờ đi qua cổng ra
currentExitContext = None
currentExitLock = threading.Lock()


def set_current_exit_context(ctx):
    global currentExitContext
    with currentExitLock:
        currentExitContext = ctx.copy() if ctx else None
    if ctx:
        save_cache("currentExitContext", ctx)
    else:
        clear_cache("currentExitContext")



def get_current_exit_context():
    with currentExitLock:
        return currentExitContext.copy() if currentExitContext else None


def clear_current_exit_context():
    global currentExitContext
    with currentExitLock:
        currentExitContext = None
    clear_cache("currentExitContext")


# =====================================================
# CAMERA LOCK
# → ĐẢM BẢO CHỈ 1 AI ĐƯỢC DÙNG CAMERA TẠI 1 THỜI ĐIỂM
# =====================================================
camera_lock = threading.Lock()

def safe_scan_plate(cam):
    with camera_lock:
        return scan_plate(cam)


def safe_face_checkin():
    with camera_lock:
        return check_in_face(entry_camera)


def safe_face_checkout(face_entry_path):
    with camera_lock:
        return check_out_face(face_entry_path, exit_camera)

# =====================================================
# RFID STATE CHECK
# → RFID ĐÃ ENTRY CHƯA
# =====================================================
def rfid_is_inside(rfid):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1
            FROM parkinghistory
            WHERE RFID=%s AND TimeOut IS NULL
            LIMIT 1
        """, (rfid,))
        return cur.fetchone() is not None

# =====================================================
# ENTRY WORKER: LPR → FACE → OPEN ENTRY
# =====================================================
def entry_worker(rfid):
    global pendingEntry

    # --- LPR ---
    log("🧠 LPR CHECK-IN START")
    img_entry, _, plate_entry = safe_scan_plate(entry_camera)
    if not plate_entry:
        write_log("ENTRY", "LPR_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_ENTRY")
        log("⛔ ENTRY LPR FAIL")
        return

    # --- FACE CHECK-IN ---
    log("🧠 FACE CHECK-IN START")
    face_res = safe_face_checkin()
    if not face_res or not face_res["success"]:
        write_log("ENTRY", "FACE_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_ENTRY")
        log("⛔ ENTRY FACE FAIL")
        return

    face_path = face_res["image_path"]

    # --- LƯU LỊCH SỬ VÀO ---
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO parkinghistory
            (RFID, TimeIn, ImageFullEntry, PlateNumberEntry, FaceImageEntry)
            VALUES (%s, NOW(), %s, %s, %s)
        """, (rfid, img_entry, plate_entry, face_path))

    # --- OPEN GATE ---
    client.publish("parking/gate/cmd", "OPEN_ENTRY")
    write_log("ENTRY", "OPEN", rfid)
    find_path_by_slot("Entry")
    log("🚪 OPEN_ENTRY")

    with state_lock:
        pendingEntry = {"rfid": rfid, "time": time.time()}
        save_cache("pendingEntry", pendingEntry) 
    log("✅ ENTRY SAVED")

# =====================================================
# EXIT WORKER: LPR → FACE → CREATE PAYMENT
# =====================================================
def exit_worker(rfid, history_id, slot_id, entry_plate, face_entry_path):
    # --- LPR EXIT ---
    log("🧠 LPR CHECK START")
    img_exit, _, plate_exit = safe_scan_plate(exit_camera)
    if not plate_exit:
        write_log("EXIT", "LPR_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        log("⛔ EXIT LPR FAIL")
        return

    # 🟢 SỬA TẠI ĐÂY: Bọc norm_plate() cho CẢ HAI bên để triệt tiêu toàn bộ dấu cách, gạch ngang
    cleaned_plate_entry = norm_plate(entry_plate)
    cleaned_plate_exit = norm_plate(plate_exit)

    log(f"🔍 Đối soát biển số: [VÀO: {cleaned_plate_entry}] vs [RA: {cleaned_plate_exit}]")

    if cleaned_plate_entry and cleaned_plate_exit != cleaned_plate_entry:
        write_log("EXIT", "LPR_MISMATCH", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        log(f"⛔ EXIT LPR MISMATCH ({cleaned_plate_exit} != {cleaned_plate_entry})")
        return

    # --- FACE CHECK-OUT (MATCH ĐÚNG NGƯỜI ENTRY) ---
    log("🧠 FACE CHECK START")
    face_res = safe_face_checkout(face_entry_path)
    if not face_res or not face_res["success"]:
        write_log("EXIT", "FACE_MISMATCH", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        log("⛔ EXIT FACE FAIL")
        return

    face_path = face_res["image_path"]

    # --- CẬP NHẬT LỊCH SỬ RA ---
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE parkinghistory
            SET
                ImageFullExit = %s,
                PlateNumberExit = %s,
                FaceImageExit = %s
            WHERE HistoryID = %s
        """, (img_exit, plate_exit, face_path, history_id))

    # --- TÍNH PHÍ ---
    with conn.cursor() as cur:
        cur.execute("""
            SELECT TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) AS minutes
            FROM parkinghistory
            WHERE HistoryID=%s
            LIMIT 1
        """, (history_id,))
        m = cur.fetchone()

    minutes = m["minutes"] if m and m["minutes"] else 0
    hours = max(1, (minutes + 59) // 60)
    fee = hours * 30000

    # --- TRÁNH DUPLICATE PAYMENT ---
    with conn.cursor() as cur:
        cur.execute("""
            SELECT PaymentID FROM payments
            WHERE HistoryID=%s
            LIMIT 1
        """, (history_id,))
        existing_payment = cur.fetchone()
        
        if existing_payment:
            log(f"ℹ PAYMENT already exists for HISTORY {history_id}")
            set_current_exit_context({
                "rfid": rfid,
                "history_id": history_id,
                "slot_id": slot_id,
                "payment_id": existing_payment["PaymentID"]
            })
            return

    # --- INSERT PAYMENT ---
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO payments (RFID, HistoryID, Amount)
            VALUES (%s, %s, %s)
        """, (rfid, history_id, fee))

        paymentId = cur.lastrowid

    set_current_exit_context({
        "rfid": rfid,
        "history_id": history_id,
        "slot_id": slot_id,
        "payment_id": paymentId
    })

    log(f"💳 PAYMENT CREATED: {paymentId} | RFID {rfid} | Fee {fee}")

# =====================================================
# PAYMENT CHECK (DB → MQTT)
# =====================================================
def check_paid_and_open():
    try:
        ctx = get_current_exit_context()
        if not ctx:
            return

        conn = get_db_connection()
        with conn.cursor() as cur:
            # 🟢 Thêm trường Amount vào câu lệnh SELECT để lấy số tiền đã thanh toán
            cur.execute("""
                SELECT PaymentID, RFID, HistoryID, Amount
                FROM payments
                WHERE HistoryID=%s
                  AND RFID=%s
                  AND Status='paid'
                  AND Notified=0
                ORDER BY PaymentID DESC
                LIMIT 1
            """, (ctx["history_id"], ctx["rfid"]))
            row = cur.fetchone()

        if not row:
            return

        paymentId = row["PaymentID"]
        rfid = row["RFID"]
        history_id = row["HistoryID"]
        paid_amount = row["Amount"]  # 🟢 Lưu giá trị tiền đã thanh toán

        log(f"💰 Payment detected: {paymentId} | RFID {rfid} | Amount {paid_amount}")

        # 🟢 TIẾN HÀNH CẬP NHẬT NGAY GIÁ TRỊ FEE VÀO LỊCH SỬ SỬ DỤNG
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE parkinghistory
                SET Fee = %s
                WHERE HistoryID = %s
            """, (paid_amount, history_id))
        log(f"📝 [Đồng bộ Fee] Đã ghi nhận số tiền {paid_amount} vào parkinghistory ID {history_id}")


        client.publish("parking/gate/cmd", "OPEN_EXIT")
        # write_log("ENTRY", "OPEN", rfid)
        write_log("EXIT", "OPEN", rfid)
        find_path_by_slot("")
        log("🚪 OPEN_EXIT SUCCESS")

        # ===== MARK AS PROCESSED =====
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE payments
                SET Notified=1
                WHERE PaymentID=%s
            """, (paymentId,))

    except Exception as e:
        log(f"❌ PAYMENT CHECK ERROR: {e}")
        # 🟢 SỬA TẠI ĐÂY: Nếu lỗi mất kết nối MySQL (Mã lỗi 2013 hoặc 'Lost connection')
        if "2013" in str(e) or "Lost connection" in str(e) or "link" in str(e).lower():
            global _db_connection
            with db_lock:
                try:
                    if _db_connection:
                        _db_connection.close()
                except:
                    pass
                _db_connection = None # Reset về None để lượt sau get_db_connection() ép tạo kết nối mới tinh
                log("🔌 [Database Recovery] Đã hủy kết nối lỗi, sẵn sàng tái tạo ở chu kỳ sau.")

        
def send_web_heartbeat(mqtt_client):
    global _db_connection
    while True:
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            mqtt_client.publish("parking/system/heartbeat", "ALIVE")
        except Exception as e:
            log(f"⚠ Web/DB đang lỗi, dừng gửi heartbeat: {e}")
            # 🟢 SỬA TẠI ĐÂY: Giải phóng kết nối lỗi để luồng Heartbeat không bị treo cứng
            with db_lock:
                _db_connection = None 
        time.sleep(3)

# =====================================================
# MQTT MESSAGE HANDLER
# =====================================================
def on_message(mqtt_client, userdata, msg):
    global pendingEntry
    
    if time.time() - START_SYSTEM_TIME < 5.0:
        if "status" in msg.topic or "log" in msg.topic:
            return 

    topic = msg.topic
    payload = msg.payload.decode().strip()
    # 🎯 BỘ LỌC ẨN LOG HEARTBEAT:
    if topic != "parking/system/heartbeat":
        log(f"📩 [{topic}] {payload}")

    try:
        # -------- IR SENSOR --------
        if topic == "parking/gate/entry/ir":
            with state_lock:
                irStatus["ENTRY"] = payload
            return

        if topic == "parking/gate/exit/ir":
            with state_lock:
                previous = irStatus["EXIT"]
                irStatus["EXIT"] = payload

            # Xe vừa đi qua cổng (O → X)
            if previous == "O" and payload == "X":
                ctx = get_current_exit_context()
                if not ctx:
                    log("⚠ Không có xe nào đang chờ ở cổng ra để chốt lịch sử.")
                    return

                rfid_exit = ctx["rfid"]
                history_id = ctx["history_id"]
                slot_id = ctx.get("slot_id")

                # 🟢 GIẢI PHÁP AN TOÀN LUỒNG: Bọc chặt chẽ bằng Try/Finally để đảm bảo Cursor không bị kẹt hay nghẽn đóng
                conn = get_db_connection()
                cur = conn.cursor() # Khởi tạo cursor thủ công để kiểm soát việc đóng/mở độc lập
                try:
                    # 1. Kiểm tra trạng thái thanh toán
                    cur.execute("""
                        SELECT Status FROM payments 
                        WHERE HistoryID = %s AND RFID = %s
                        ORDER BY PaymentID DESC LIMIT 1
                    """, (history_id, rfid_exit))
                    payment_row = cur.fetchone()

                    if not payment_row or payment_row["Status"] != "paid":
                        log(f"⛔ CHẶN CHỐT LỊCH SỬ: Xe RFID {rfid_exit} chưa hoàn thành thủ tục xuất bãi hợp lệ!")
                        return

                    # 2. Tiến hành cập nhật lịch sử ra
                    cur.execute("""
                        UPDATE parkinghistory
                        SET TimeOut = NOW(),
                            Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW())
                        WHERE HistoryID=%s
                    """, (history_id,))
                    log(f"🕒 [Chốt giờ ra] HỢP LỆ! Đã ghi nhận TimeOut cho HistoryID: {history_id}")

                    # 3. Cập nhật giải phóng chuồng (nếu có)
                    if slot_id is not None:
                        cur.execute("""
                            UPDATE parkingslot
                            SET Status=0, CurrentRFID=NULL
                            WHERE SlotID=%s
                        """, (slot_id,))
                        log(f"⬜ [Giải phóng chuồng] Đã dọn trống SlotID: {slot_id}")

                    # Chỉ xóa context khi mọi câu lệnh SQL trên đã thực thi thành công hoàn toàn
                    clear_current_exit_context()
                    log(f"🚗 EXIT COMPLETE | RFID {rfid_exit} đã rời bãi thành công!")

                except Exception as db_err:
                    log(f"❌ LỖI TRONG QUÁ TRÌNH UPDATE LỊCH SỬ IR: {db_err}")
                finally:
                    try:
                        cur.close() # 🟢 ĐẢM BẢO LUÔN ĐÓNG CURSOR DÙ CÓ LỖI HAY KHÔNG, tránh lỗi Cursor closed cho lượt sau
                    except:
                        pass
            return
        
        # -------- OFFLINE LOG SYNC FROM WEMOS --------
        if topic == "parking/log":
            try:
                log_data = json.loads(payload)
                event_type = log_data.get("event")
                slot_id = log_data.get("slot")
                status = log_data.get("status")
                
                if event_type == "slot_change" and slot_id:
                    db_status = 1 if status == "O" else 0
                    area = slot_id[0]      
                    slot_code = slot_id[1:] 
                    
                    conn = get_db_connection()
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE parkingslot 
                            SET Status=%s 
                            WHERE Area=%s AND SlotCode=%s
                        """, (db_status, area, slot_code))
                        
                    # 🛑 BẢO MẬT: ĐÃ XÓA HOÀN TOÀN ĐOẠN CODE TỰ ĐIỀN TIMEOUT SAI TRÁI TẠI ĐÂY!
                    # Chuồng trống hay đầy chỉ dùng để đổi màu map hệ thống, không tự chốt TimeOut lịch sử bừa bãi.
                return
            except Exception as json_err:
                log(f"⚠ Lỗi parse JSON parking/log: {json_err}")
                return

        # -------- SLOT STATUS --------
        m = re.match(r"^parking/slot/([A-Z])(\d+)/status$", topic)
        if m:
            area, slotCode = m.group(1), m.group(2)
            status = payload

            slot_key = f"{area}{slotCode}"

            with state_lock:
                is_duplicate = slotStatus.get(slot_key) == status
                if not is_duplicate:
                    slotStatus[slot_key] = status


            if is_duplicate:
                log(f"⏭ Duplicate slot state {slot_key} = {status} → skip")
                return

            log(f"📌 SLOT UPDATE: {slot_key} = {status}")
            conn = get_db_connection()


            if status == "O":
                find_path_by_slot("")
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=1
                        WHERE Area=%s AND SlotCode=%s
                    """, (area, slotCode))

                with state_lock:
                    rfid = pendingEntry["rfid"] if pendingEntry else None

                if not rfid:
                    with conn.cursor() as cur:

                        cur.execute("""
                            SELECT RFID FROM parkinghistory
                            WHERE TimeOut IS NULL
                            ORDER BY TimeIn DESC

                            LIMIT 1
                        """)
                        row = cur.fetchone()
                        if not row:
                            log(f"⚠ No RFID for {slot_key}")

                            return
                        rfid = row["RFID"]

                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT SlotID FROM parkingslot
                        WHERE Area=%s AND SlotCode=%s
                        LIMIT 1
                    """, (area, slotCode))
                    slot_row = cur.fetchone()

                    if not slot_row:
                        log(f"❌ SLOT NOT FOUND: {slot_key}")
                        return
                    slotId = slot_row["SlotID"]


                    cur.execute("""
                        UPDATE parkinghistory
                        SET SlotID=%s
                        WHERE RFID=%s AND TimeOut IS NULL
                        ORDER BY HistoryID DESC
                        LIMIT 1
                    """, (slotId, rfid))

                    cur.execute("""
                        UPDATE parkingslot
                        SET CurrentRFID=%s
                        WHERE SlotID=%s
                    """, (rfid, slotId))

                with state_lock:
                    pendingEntry = None
                    clear_cache("pendingEntry") 
                log(f"✅ SLOT {slot_key} ASSIGNED TO {rfid}")
                return

            if status == "X":
                find_path_by_slot(slot_key)
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=0, CurrentRFID=NULL
                        WHERE Area=%s AND SlotCode=%s
                    """, (area, slotCode))
                log(f"⬜ SLOT {slot_key} CLEARED")
                return

        # -------- RFID --------
        if topic != "parking/rfid":
            return

        m = re.match(r"^(ENTRY|EXIT):(.+)$", payload)
        if not m:
            return

        gateType, rfid = m.group(1), m.group(2).strip()

        with state_lock:
            ir_cond = irStatus.get(gateType) == "X"
        if ir_cond:
            return

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM rfidcard WHERE RFID=%s", (rfid,))
            if not cur.fetchone():
                write_log(gateType, "RFID_INVALID", rfid)
                return

        # -------- ENTRY --------
        if gateType == "ENTRY":
            if rfid_is_inside(rfid):
                write_log("ENTRY", "ALREADY_INSIDE", rfid)
                client.publish("parking/gate/cmd", "DENY_ENTRY")
                return

            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS free FROM parkingslot WHERE Status=0")
                if cur.fetchone()["free"] == 0:
                    write_log("ENTRY", "PARKING_FULL", rfid)
                    client.publish("parking/gate/cmd", "DENY_ENTRY")
                    return

            threading.Thread(target=entry_worker, args=(rfid,), daemon=True).start()

            return

        # -------- EXIT --------
        if gateType == "EXIT":
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT HistoryID, SlotID, PlateNumberEntry, FaceImageEntry
                    FROM parkinghistory
                    WHERE RFID=%s AND TimeOut IS NULL
                    ORDER BY HistoryID DESC
                    LIMIT 1
                """, (rfid,))
                row = cur.fetchone()

            if not row:
                write_log("EXIT", "NO_ACTIVE_ENTRY", rfid)
                return

            set_current_exit_context({
                "rfid": rfid,
                "history_id": row["HistoryID"],
                "slot_id": row["SlotID"]
            })

            threading.Thread(
                target=exit_worker,
                args=(rfid, row["HistoryID"], row["SlotID"], norm_plate(row["PlateNumberEntry"]), row["FaceImageEntry"]),

                daemon=True
            ).start()
            return

    except Exception as e:
        log(f"❌ ERROR in on_message: {e}")

# =====================================================
# FLASK WEB SERVER (MJPEG STREAM)
# =====================================================
app = Flask(__name__)


def generate_frames(cam):
    """Generator liên tục lấy ảnh JPEG từ CameraService và đóng gói thành MJPEG"""
    while True:
        frame_bytes = cam.get_mjpeg_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1) # Nếu không có frame, đợi 1 chút


@app.route('/video_feed_entry')
def video_feed_entry():
    """API Endpoint để web PHP gọi tới thẻ <img>"""
    return Response(generate_frames(entry_camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_exit')
def video_feed_exit():
    """API Endpoint để web PHP gọi tới thẻ <img>"""
    return Response(generate_frames(exit_camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
def get_logs():
    """API Endpoint để lấy logs terminal hiển thị lên frontend"""
    resp = Response(json.dumps(list(log_buffer)), mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/admin/force-checkout/<int:history_id>', methods=['POST'])
def admin_force_checkout(history_id):
    try:
        conn = get_db_connection()
        
        # Lấy thông tin lượt xe kẹt
        with conn.cursor() as cur:
            cur.execute("""
                SELECT RFID, SlotID, TimeIn 
                FROM parkinghistory 
                WHERE HistoryID = %s AND TimeOut IS NULL
            """, (history_id,))
            row = cur.fetchone()
            
        if not row:
            return jsonify({"success": False, "message": "Xe đã ra hoặc không tồn tại!"}), 400
            
        rfid = row["RFID"]
        slot_id = row["SlotID"]
        time_in = row["TimeIn"]
        
        # Tính phí tượng trưng hoặc tính theo giờ thực tế (Tùy bạn cấu hình, ở đây tính thực tế)
        duration = int((datetime.now() - time_in).total_seconds() / 60)
        hours = max(1, (duration + 59) // 60)
        fee = hours * 30000
        
        with conn.cursor() as cur:
            # 1. Ép chốt đóng lịch sử bằng tay
            cur.execute("""
                UPDATE parkinghistory
                SET TimeOut = NOW(),
                    Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()),
                    Fee = %s,
                    PlateNumberExit = 'ADMIN_MANUAL'
                WHERE HistoryID = %s
            """, (fee, history_id))
            
            # 2. Giải phóng chuồng (nếu trước đó xe đã kịp vào chuồng)
            if slot_id:
                cur.execute("""
                    UPDATE parkingslot
                    SET Status = 0, CurrentRFID = NULL
                    WHERE SlotID = %s
                """, (slot_id,))
                
            # 3. Tạo hóa đơn đã thu tiền bởi Admin
            cur.execute("""
                INSERT INTO payments (RFID, HistoryID, Amount, Status, Notified)
                VALUES (%s, %s, %s, 'paid', 1)
            """, (rfid, history_id, fee))
            
        log(f"👮‍♂️ [ADMIN] Đã giải phóng thủ công xe mồ côi/kẹt nguồn: {rfid}")
        find_path_by_slot("") # Cập nhật lại sơ đồ bãi xe
        
        return jsonify({"success": True, "message": "Đã giải phóng xe và làm sạch thẻ thành công!"}), 200
        
    except Exception as e:
        log(f"❌ Lỗi Admin checkout: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# =====================================================
# START INITIALIZATION & CRASH RECOVERY
# =====================================================
client.on_message = on_message
client.subscribe("parking/#")
log("➡ Subscribed parking/#")

try:
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT Area, SlotCode, Status FROM parkingslot")
        rows = cur.fetchall()
        with state_lock:
            for row in rows:
                key = f"{row['Area']}{row['SlotCode']}"
                slotStatus[key] = "O" if row['Status'] == 1 else "X"
    log(f"📊 Đồng bộ trạng thái ban đầu từ DB thành công")
except Exception as e:
    log(f"⚠ Không thể lấy trạng thái ban đầu từ DB: {e}")

log("🔄 Đang quét dữ liệu khôi phục (Crash Recovery)...")
saved_exit_ctx = load_cache("currentExitContext")
if saved_exit_ctx:
    with currentExitLock:
        currentExitContext = saved_exit_ctx
    log(f"♻ [Hồi sinh] Khôi phục xe đang chờ lối RA: RFID {saved_exit_ctx.get('rfid')}")

saved_pending_entry = load_cache("pendingEntry")
if saved_pending_entry:
    with state_lock:
        pendingEntry = saved_pending_entry
    log(f"♻ [Hồi sinh] Khôi phục xe vừa quẹt lối VÀO: RFID {saved_pending_entry.get('rfid')}")

# =====================================================
# HTTP REALTIME HARDWARE SYNC
# =====================================================
def sync_hardware_realtime():
    wemos_url = "http://172.16.10.172/status"
    log(f"🌐 [HTTP Sync] Kết nối tới phần cứng {wemos_url}...")
    try:
        response = requests.get(wemos_url, timeout=3)
        if response.status_code == 200:
            hardware_data = response.json()
            log(f"📥 Hiện trạng từ Wemos: {hardware_data}")
            
            conn = get_db_connection()
            for slot_key, status in hardware_data.items():
                area = slot_key[0]       
                slot_code = slot_key[1:] 
                db_status = 1 if status == "O" else 0
                
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE parkingslot 
                        SET Status=%s 
                        WHERE Area=%s AND SlotCode=%s
                    """, (db_status, area, slot_code))
                
                with state_lock:
                    slotStatus[slot_key] = status
            log(f"⚡ [HTTP Sync] Khởi tạo đồng bộ phần cứng hoàn tất!")
    except Exception as e:
        log(f"⚠ Bỏ qua HTTP Sync: {e}. Hệ thống vận hành bằng MQTT.")

sync_hardware_realtime()
# =====================================================

client.loop_start()
threading.Thread(target=send_web_heartbeat, args=(client,), daemon=True).start()

# Thêm dòng này ngay TRƯỚC KHI khởi chạy Flask Thread để ép tắt log Werkzeug
logging.getLogger('werkzeug').setLevel(logging.ERROR)
flask_thread = threading.Thread(
    target=lambda: app.run(host='0.0.0.0', port=5001, threaded=True, use_reloader=False),
    daemon=True
)
flask_thread.start()
log("🌐 Flask Web Stream started on http://0.0.0.0:5001/video_feed_entry and /video_feed_exit")

try:
    while True:
        check_paid_and_open()
        time.sleep(2)
except KeyboardInterrupt:
    log("🛑 KeyboardInterrupt")
finally:
    log("📷 Releasing camera")
    entry_camera.release()
    exit_camera.release()
    try:
        if _db_connection:
            _db_connection.close()
    except:
        pass
    log("👋 Shutdown complete")