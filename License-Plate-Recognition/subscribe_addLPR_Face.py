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

from plate_scanner import scan_plate
from face_detect_deepface_faster import check_in_face, check_out_face
from camera import camera
from path_finder import find_path_by_slot

# O: Occupied, X: Empty
# 1: Occupied, 0: Empty
# =====================================================
# CONSOLE LOG
# =====================================================
log_buffer = deque(maxlen=50)

def log(msg):
    log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(log_line, flush=True)
    log_buffer.append(log_line)


def norm_plate(p):
    if not p:
        return None
    return p.replace(" ", "").replace("-", "").upper()

# =====================================================
# DB CONNECTION
# =====================================================
db = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="smart_parking",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
log("✅ DB connected")

# =====================================================
# GATE LOG (LƯU SỰ KIỆN ĐÓNG / MỞ / TỪ CHỐI)
# =====================================================
def write_log(gate, action, triggered_by):
    try:
        with db.cursor() as cur:
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
slotStatus = {}  # 🚀 FIX: lưu trạng thái cuối của slot
pendingEntry = None   # RFID vừa vào, dùng để gán slot chính xác

# Xe đang chờ thanh toán và chờ đi qua cổng ra
currentExitContext = None
currentExitLock = threading.Lock()


def set_current_exit_context(ctx):
    global currentExitContext
    with currentExitLock:
        currentExitContext = ctx.copy() if ctx else None


def get_current_exit_context():
    with currentExitLock:
        return currentExitContext.copy() if currentExitContext else None


def clear_current_exit_context():
    global currentExitContext
    with currentExitLock:
        currentExitContext = None

# =====================================================
# CAMERA LOCK
# → ĐẢM BẢO CHỈ 1 AI ĐƯỢC DÙNG CAMERA TẠI 1 THỜI ĐIỂM
# =====================================================
camera_lock = threading.Lock()


def safe_scan_plate():
    with camera_lock:
        return scan_plate()


def safe_face_checkin():
    with camera_lock:
        return check_in_face()


def safe_face_checkout(face_entry_path):
    with camera_lock:
        return check_out_face(face_entry_path)

# =====================================================
# RFID STATE CHECK
# → RFID ĐÃ ENTRY CHƯA
# =====================================================
def rfid_is_inside(rfid):
    with db.cursor() as cur:
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
    img_entry, _, plate_entry = safe_scan_plate()
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

    pendingEntry = {"rfid": rfid, "time": time.time()}
    log("✅ ENTRY SAVED")

# =====================================================
# EXIT WORKER: LPR → FACE → CREATE PAYMENT
# =====================================================
def exit_worker(rfid, history_id, slot_id, entry_plate, face_entry_path):
    # --- LPR EXIT ---
    log("🧠 LPR CHECK START")
    img_exit, _, plate_exit = safe_scan_plate()
    if not plate_exit:
        write_log("EXIT", "LPR_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        log("⛔ EXIT LPR FAIL")
        return

    if entry_plate and norm_plate(plate_exit) != entry_plate:
        write_log("EXIT", "LPR_MISMATCH", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        log("⛔ EXIT LPR MISMATCH")
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
    with db.cursor() as cur:
        cur.execute("""
            UPDATE parkinghistory
            SET
                ImageFullExit = %s,
                PlateNumberExit = %s,
                FaceImageExit = %s
            WHERE HistoryID = %s
        """, (img_exit, plate_exit, face_path, history_id))

    # --- TÍNH PHÍ ---
    with db.cursor() as cur:
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
    with db.cursor() as cur:
        cur.execute("""
            SELECT PaymentID FROM payments
            WHERE HistoryID=%s
            LIMIT 1
        """, (history_id,))
        if cur.fetchone():
            log(f"ℹ PAYMENT already exists for HISTORY {history_id}")
            set_current_exit_context({
                "rfid": rfid,
                "history_id": history_id,
                "slot_id": slot_id
            })
            return

    # --- INSERT PAYMENT ---
    with db.cursor() as cur:
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

        with db.cursor() as cur:
            cur.execute("""
                SELECT PaymentID, RFID, HistoryID
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

        log(f"💰 Payment detected: {paymentId} | RFID {rfid}")

        # ===== OPEN GATE =====
        client.publish("parking/gate/cmd", "OPEN_ENTRY")#OPEN_EXIT
        client.publish("parking/gate/cmd", "OPEN_EXIT")
        # write_log("ENTRY", "OPEN", rfid)
        write_log("EXIT", "OPEN", rfid)
        find_path_by_slot("")
        # log("🚪 OPEN_ENTRY (from payment)")#OPEN_EXIT
        log("🚪 OPEN_ENTRY + OPEN_EXIT")

        # ===== MARK AS PROCESSED =====
        with db.cursor() as cur:
            cur.execute("""
                UPDATE payments
                SET Notified=1
                WHERE PaymentID=%s
            """, (paymentId,))

    except Exception as e:
        log(f"❌ PAYMENT CHECK ERROR: {e}")

# =====================================================
# MQTT MESSAGE HANDLER
# =====================================================
def on_message(client, userdata, msg):
    global pendingEntry

    topic = msg.topic
    payload = msg.payload.decode().strip()
    log(f"📩 [{topic}] {payload}")

    try:
        # -------- IR SENSOR --------
        if topic == "parking/gate/entry/ir":
            irStatus["ENTRY"] = payload
            return

        if topic == "parking/gate/exit/ir":
            previous = irStatus["EXIT"]
            irStatus["EXIT"] = payload

            # Xe vừa đi qua cổng (O → X)
            if previous == "O" and payload == "X":
                ctx = get_current_exit_context()
                if not ctx:
                    log("⚠ No active exit context")
                    return

                rfid_exit = ctx["rfid"]
                history_id = ctx["history_id"]
                slot_id = ctx["slot_id"]

                with db.cursor() as cur:
                    # ===== 1. UPDATE TIMEOUT CHÍNH XÁC THEO HISTORYID =====
                    cur.execute("""
                        UPDATE parkinghistory
                        SET TimeOut = NOW(),
                            Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW())
                        WHERE HistoryID=%s
                    """, (history_id,))

                    # ===== 2. LẤY PAYMENT ĐÃ TRẢ THEO HISTORYID =====
                    cur.execute("""
                        SELECT Amount
                        FROM payments
                        WHERE HistoryID=%s AND Status='paid'
                        ORDER BY PaymentID DESC
                        LIMIT 1
                    """, (history_id,))
                    p = cur.fetchone()

                    # ===== LUÔN SET FEE =====
                    if p:
                        fee_value = p["Amount"]
                    else:
                        # fallback nếu payment chưa có
                        cur.execute("""
                            SELECT TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) AS minutes
                            FROM parkinghistory
                            WHERE HistoryID=%s
                        """, (history_id,))
                        m2 = cur.fetchone()
                        minutes2 = m2["minutes"] if m2 and m2["minutes"] else 0
                        hours2 = (minutes2 + 59) // 60
                        fee_value = hours2 * 30000

                    cur.execute("""
                        UPDATE parkinghistory
                        SET Fee=%s
                        WHERE HistoryID=%s
                    """, (fee_value, history_id))

                    # ===== 3. FREE SLOT CHÍNH XÁC =====
                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=0, CurrentRFID=NULL
                        WHERE SlotID=%s
                    """, (slot_id,))

                clear_current_exit_context()
                log(f"🚗 EXIT COMPLETE | RFID {rfid_exit}")

            return

        # -------- SLOT STATUS --------
        # -------- SLOT STATUS --------
        m = re.match(r"^parking/slot/([A-Z])(\d+)/status$", topic)
        if m:
            area, slotCode = m.group(1), m.group(2)
            status = payload

            slot_key = f"{area}{slotCode}"

            # 🚀 FIX 1: tránh xử lý lặp + giữ trạng thái cuối
            if slotStatus.get(slot_key) == status:
                log(f"⏭ Duplicate slot state {slot_key} = {status} → skip only slot handling")
                pass
            else:
                slotStatus[slot_key] = status

                log(f"📌 SLOT UPDATE: {slot_key} = {status}")

                # ===== SLOT OCCUPIED =====
                if status == "O":
                    find_path_by_slot("")

                    with db.cursor() as cur:
                        # 🔥 LUÔN UPDATE SLOT TRƯỚC (QUAN TRỌNG NHẤT)
                        cur.execute("""
                            UPDATE parkingslot
                            SET Status=1
                            WHERE Area=%s AND SlotCode=%s
                        """, (area, slotCode))

                    # ===== GIỮ NGUYÊN LOGIC RFID (KHÔNG ĐỤNG) =====
                    rfid = pendingEntry["rfid"] if pendingEntry else None

                    if not rfid:
                        with db.cursor() as cur:
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

                    with db.cursor() as cur:
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

                    pendingEntry = None
                    log(f"✅ SLOT {slot_key} ASSIGNED TO {rfid}")
                    return

                # ===== SLOT EMPTY =====
                if status == "X":
                    find_path_by_slot(slot_key)

                    with db.cursor() as cur:
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

        # IR chỉ chặn khi đang X
        if irStatus.get(gateType) == "X":
            return

        # RFID hợp lệ?
        with db.cursor() as cur:
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

            with db.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS free FROM parkingslot WHERE Status=0")
                if cur.fetchone()["free"] == 0:
                    write_log("ENTRY", "PARKING_FULL", rfid)
                    client.publish("parking/gate/cmd", "DENY_ENTRY")
                    return

            threading.Thread(
                target=entry_worker,
                args=(rfid,),
                daemon=True
            ).start()
            return

        # -------- EXIT --------
        if gateType == "EXIT":
            with db.cursor() as cur:
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
                args=(
                    rfid,
                    row["HistoryID"],
                    row["SlotID"],
                    norm_plate(row["PlateNumberEntry"]),
                    row["FaceImageEntry"]
                ),
                daemon=True
            ).start()
            return

    except Exception as e:
        log(f"❌ ERROR: {e}")

# =====================================================
# FLASK WEB SERVER (MJPEG STREAM)
# =====================================================
app = Flask(__name__)


def generate_frames():
    """Generator liên tục lấy ảnh JPEG từ CameraService và đóng gói thành MJPEG"""
    while True:
        frame_bytes = camera.get_mjpeg_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1) # Nếu không có frame, đợi 1 chút


@app.route('/video_feed')
def video_feed():
    """API Endpoint để web PHP gọi tới thẻ <img>"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/logs')
def get_logs():
    """API Endpoint để lấy logs terminal hiển thị lên frontend"""
    resp = Response(json.dumps(list(log_buffer)), mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# =====================================================
# START
# =====================================================
client.on_message = on_message
client.subscribe("parking/#")
log("➡ Subscribed parking/#")

client.loop_start()

# --- BẬT FLASK SERVER TRONG LUỒNG PHỤ ---
flask_thread = threading.Thread(
    target=lambda: app.run(host='0.0.0.0', port=5001, threaded=True, use_reloader=False),
    daemon=True
)
flask_thread.start()
log("🌐 Flask Web Stream started on http://0.0.0.0:5001/video_feed")

try:
    while True:
        check_paid_and_open()
        time.sleep(2)
except KeyboardInterrupt:
    log("🛑 KeyboardInterrupt")
finally:
    log("📷 Releasing camera")
    camera.release()
    try:
        db.close()
    except:
        pass
    log("👋 Shutdown complete")