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

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="smart_parking",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
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
    finally:
        if conn:
            conn.close()

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
    finally:
        if conn:
            conn.close()
    return None

def clear_cache(key):
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            cur.execute("DELETE FROM system_cache WHERE cache_key=%s", (key,))
    except Exception as e:
        log(f"⚠ Không thể xóa cache {key}: {e}")
    finally:
        if conn:
            conn.close()

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
    finally:
        if conn:
            conn.close()

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
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1
                FROM parkinghistory
                WHERE RFID=%s AND TimeOut IS NULL
                LIMIT 1
            """, (rfid,))
            return cur.fetchone() is not None
    finally:
        if conn:
            conn.close()

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
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO parkinghistory
                (RFID, TimeIn, ImageFullEntry, PlateNumberEntry, FaceImageEntry)
                VALUES (%s, NOW(), %s, %s, %s)
            """, (rfid, img_entry, plate_entry, face_path))

        conn.commit()
    finally:
        if conn:
            conn.close()

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

    paymentId = None
    conn = None

    # --- LPR ---
    log("🧠 LPR CHECK START")
    img_exit, _, plate_exit = safe_scan_plate(exit_camera)

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

    # --- FACE ---
    log("🧠 FACE CHECK START")
    face_res = safe_face_checkout(face_entry_path)

    if not face_res or not face_res["success"]:
        write_log("EXIT", "FACE_MISMATCH", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        log("⛔ EXIT FACE FAIL")
        return

    face_path = face_res["image_path"]

    # --- DB ---
    try:
        conn = get_db_connection()

        # 1. update history exit info
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE parkinghistory
                SET ImageFullExit=%s,
                    PlateNumberExit=%s,
                    FaceImageExit=%s
                WHERE HistoryID=%s
            """, (img_exit, plate_exit, face_path, history_id))

        # 2. get duration
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) AS minutes
                FROM parkinghistory
                WHERE HistoryID=%s
            """, (history_id,))
            row = cur.fetchone()

        minutes = row["minutes"] if row and row["minutes"] else 0
        hours = max(1, (minutes + 59) // 60)
        fee = hours * 30000

        # 3. check duplicate payment
        with conn.cursor() as cur:
            cur.execute("""
                SELECT PaymentID
                FROM payments
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

        # 4. insert payment
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO payments (RFID, HistoryID, Amount)
                VALUES (%s, %s, %s)
            """, (rfid, history_id, fee))

            paymentId = cur.lastrowid

    finally:
        if conn:
            conn.close()

    # --- SAFE: chỉ chạy khi paymentId chắc chắn tồn tại ---
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
    conn = None

    try:
        conn = get_db_connection()
        conn.ping(reconnect=True)

        ctx = get_current_exit_context()
        if not ctx:
            return

        # =====================================================
        # CHECK PAYMENT
        # =====================================================
        with conn.cursor() as cur:
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
        paid_amount = row["Amount"]

        log(f"💰 Payment detected: {paymentId} | RFID {rfid} | Amount {paid_amount}")

        # =====================================================
        # UPDATE FEE ONLY (KHÔNG UPDATE DURATION)
        # =====================================================
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE parkinghistory
                SET Fee=%s
                WHERE HistoryID=%s
                  AND TimeOut IS NULL
            """, (paid_amount, history_id))

        log(f"📝 Fee updated for HistoryID {history_id}")

        conn.commit()

        # =====================================================
        # OPEN GATE
        # =====================================================
        client.publish("parking/gate/cmd", "OPEN_EXIT")

        write_log("EXIT", "OPEN", rfid)

        find_path_by_slot("")

        log("🚪 OPEN_EXIT SUCCESS")

        # =====================================================
        # MARK PAYMENT PROCESSED
        # =====================================================
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE payments
                SET Notified=1
                WHERE PaymentID=%s
            """, (paymentId,))

        conn.commit()

        log(f"✅ Payment {paymentId} marked as notified")

    except Exception as e:
        log(f"❌ PAYMENT CHECK ERROR: {e}")

    finally:
        if conn:
            conn.close()
                    
def send_web_heartbeat(mqtt_client):
    while True:
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            mqtt_client.publish("parking/system/heartbeat", "ALIVE")
        except Exception as e:
            log(f"⚠ Web/DB đang lỗi, dừng gửi heartbeat: {e}")
        finally:
            if conn:
                conn.close()
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

        # -------- IR SENSOR --------
        if topic == "parking/gate/entry/ir":
            with state_lock:
                irStatus["ENTRY"] = payload
            return


        if topic == "parking/gate/exit/ir":
            with state_lock:
                previous = irStatus["EXIT"]
                irStatus["EXIT"] = payload

            # Xe vừa đi qua (O → X)
            if previous == "O" and payload == "X":

                # debounce chống nhiễu IR
                now = time.time()
                last = globals().get("last_exit_trigger", 0)
                if now - last < 1:
                    return
                globals()["last_exit_trigger"] = now

                # safe read context
                with currentExitLock:
                    ctx = currentExitContext.copy() if currentExitContext else None

                if not ctx:
                    log("⚠ Không có xe nào đang chờ ở cổng ra để chốt lịch sử.")
                    return

                rfid_exit = ctx["rfid"]
                history_id = ctx["history_id"]
                slot_id = ctx.get("slot_id")

                conn = None

                try:
                    conn = get_db_connection()

                    with conn.cursor() as cur:

                        # chốt history
                        cur.execute("""
                            UPDATE parkinghistory
                            SET TimeOut = NOW(),
                                Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW())
                            WHERE HistoryID=%s AND TimeOut IS NULL
                        """, (history_id,))

                        # giải phóng slot
                        if slot_id:
                            cur.execute("""
                                UPDATE parkingslot
                                SET Status=0,
                                    CurrentRFID=NULL
                                WHERE SlotID=%s
                            """, (slot_id,))

                    conn.commit()

                except Exception as e:
                    log(f"❌ EXIT IR DB ERROR: {e}")
                    if conn:
                        conn.rollback()

                finally:
                    if conn:
                        conn.close()

                clear_current_exit_context()

                log(f"🚗 EXIT COMPLETE | RFID {rfid_exit} đã rời bãi thành công!")

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

                    conn = None
                    try:
                        conn = get_db_connection()

                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE parkingslot 
                                SET Status=%s 
                                WHERE Area=%s AND SlotCode=%s
                            """, (db_status, area, slot_code))

                        conn.commit()

                    finally:
                        if conn:
                            conn.close()

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

            conn = None

            try:
                conn = get_db_connection()

                # =====================================================
                # SLOT STATUS UPDATE
                # =====================================================
                if status == "O":
                    find_path_by_slot("")

                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE parkingslot
                            SET Status=1
                            WHERE Area=%s AND SlotCode=%s
                        """, (area, slotCode))

                    # =====================================================
                    # GET RFID AN TOÀN (KHÔNG FALLBACK RANDOM DESC)
                    # =====================================================
                    with state_lock:
                        rfid = pendingEntry["rfid"] if pendingEntry else None

                    if not rfid:
                        log(f"⚠ No pendingEntry RFID for slot {slot_key}")
                        conn.commit()
                        return

                    # =====================================================
                    # GET SLOT ID
                    # =====================================================
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT SlotID 
                            FROM parkingslot
                            WHERE Area=%s AND SlotCode=%s
                            LIMIT 1
                        """, (area, slotCode))

                        slot_row = cur.fetchone()

                        if not slot_row:
                            log(f"❌ SLOT NOT FOUND: {slot_key}")
                            conn.rollback()
                            return

                        slotId = slot_row["SlotID"]

                    # =====================================================
                    # UPDATE HISTORY + SLOT LINK
                    # =====================================================
                    with conn.cursor() as cur:
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

                    conn.commit()
                    log(f"✅ SLOT {slot_key} ASSIGNED TO {rfid}")
                    return

                # =====================================================
                # SLOT CLEARED
                # =====================================================
                if status == "X":
                    find_path_by_slot(slot_key)

                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE parkingslot
                            SET Status=0, CurrentRFID=NULL
                            WHERE Area=%s AND SlotCode=%s
                        """, (area, slotCode))

                    conn.commit()
                    log(f"⬜ SLOT {slot_key} CLEARED")
                    return

            except Exception as e:
                log(f"❌ SLOT STATUS ERROR: {e}")
                if conn:
                    conn.rollback()

            finally:
                if conn:
                    conn.close()

            return

        # -------- RFID --------
        if topic != "parking/rfid":
            return

        try:
            m = re.match(r"^(ENTRY|EXIT):(.+)$", payload)
            if not m:
                return

            gateType, rfid = m.group(1), m.group(2).strip()

            # =====================================================
            # IR BLOCK CHECK
            # =====================================================
            with state_lock:
                ir_cond = irStatus.get(gateType) == "X"

            if ir_cond:
                return

            # =====================================================
            # VERIFY RFID
            # =====================================================
            conn = None

            try:
                conn = get_db_connection()

                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM rfidcard WHERE RFID=%s", (rfid,))
                    if not cur.fetchone():
                        write_log(gateType, "RFID_INVALID", rfid)
                        return

                # =====================================================
                # ENTRY FLOW
                # =====================================================
                if gateType == "ENTRY":

                    if rfid_is_inside(rfid):
                        write_log("ENTRY", "ALREADY_INSIDE", rfid)
                        client.publish("parking/gate/cmd", "DENY_ENTRY")
                        return

                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT COUNT(*) AS free 
                            FROM parkingslot 
                            WHERE Status=0
                        """)
                        free_slots = cur.fetchone()["free"]

                    if free_slots == 0:
                        write_log("ENTRY", "PARKING_FULL", rfid)
                        client.publish("parking/gate/cmd", "DENY_ENTRY")
                        return

                    # ✔ entry_worker tự quản DB riêng → OK
                    threading.Thread(
                        target=entry_worker,
                        args=(rfid,),
                        daemon=True
                    ).start()

                    return

                # =====================================================
                # EXIT FLOW
                # =====================================================
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

                    # ✔ set context BEFORE thread (atomic chuẩn)
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

            finally:
                if conn:
                    conn.close()

        except Exception as e:
            log(f"❌ ERROR in on_message RFID: {e}")

# =====================================================
# FLASK WEB SERVER (MJPEG STREAM)
# =====================================================
app = Flask(__name__)

def generate_frames(cam):
    """Generator MJPEG an toàn + chống treo stream"""
    
    while True:
        try:
            frame_bytes = cam.get_mjpeg_frame()

            if frame_bytes:
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    frame_bytes +
                    b'\r\n'
                )
            else:
                time.sleep(0.05)  # giảm latency (tốt hơn 0.1)

        except Exception as e:
            log(f"⚠ Camera stream error: {e}")
            time.sleep(1)


@app.route('/video_feed_entry')
def video_feed_entry():
    return Response(
        generate_frames(entry_camera),
        mimetype='multipart/x-mixed-replace; boundary=frame',
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
    )
    
@app.route('/video_feed_exit')
def video_feed_exit():
    return Response(
        generate_frames(exit_camera),
        mimetype='multipart/x-mixed-replace; boundary=frame',
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
    )
@app.route('/logs')
def get_logs():
    try:
        with state_lock:   # hoặc log_lock nếu bạn có
            data = list(log_buffer)

        resp = Response(
            json.dumps(data),
            mimetype='application/json'
        )

        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            mimetype='application/json',
            status=500
        )

@app.route('/admin/force-checkout/<int:history_id>', methods=['POST'])
def admin_force_checkout(history_id):
    conn = None

    try:
        conn = get_db_connection()

        # =====================================================
        # 1. GET ACTIVE HISTORY
        # =====================================================
        with conn.cursor() as cur:
            cur.execute("""
                SELECT RFID, SlotID, TimeIn 
                FROM parkinghistory 
                WHERE HistoryID = %s AND TimeOut IS NULL
            """, (history_id,))
            row = cur.fetchone()

        if not row:
            return jsonify({
                "success": False,
                "message": "Xe đã ra hoặc không tồn tại!"
            }), 400

        rfid = row["RFID"]
        slot_id = row["SlotID"]

        # =====================================================
        # 2. CALCULATE FEE (ONLY PYTHON OR SQL, chọn 1)
        # =====================================================
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) AS duration
                FROM parkinghistory
                WHERE HistoryID=%s
            """, (history_id,))
            d = cur.fetchone()["duration"] or 0

        hours = max(1, (d + 59) // 60)
        fee = hours * 30000

        # =====================================================
        # 3. ATOMIC UPDATE (HISTORY + SLOT + PAYMENT)
        # =====================================================
        with conn.cursor() as cur:

            # update history
            cur.execute("""
                UPDATE parkinghistory
                SET TimeOut = NOW(),
                    Duration = %s,
                    Fee = %s,
                    PlateNumberExit = 'ADMIN_MANUAL'
                WHERE HistoryID = %s
            """, (d, fee, history_id))

            # release slot
            if slot_id:
                cur.execute("""
                    UPDATE parkingslot
                    SET Status = 0,
                        CurrentRFID = NULL
                    WHERE SlotID = %s
                """, (slot_id,))

            # avoid duplicate payment
            cur.execute("""
                SELECT 1 FROM payments
                WHERE HistoryID=%s
                LIMIT 1
            """, (history_id,))

            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO payments (RFID, HistoryID, Amount, Status, Notified)
                    VALUES (%s, %s, %s, 'paid', 1)
                """, (rfid, history_id, fee))

        conn.commit()

        log(f"👮‍♂️ ADMIN FORCE CHECKOUT: {rfid} | Fee {fee}")
        find_path_by_slot("")

        return jsonify({
            "success": True,
            "message": "Đã giải phóng xe thành công!"
        }), 200

    except Exception as e:
        log(f"❌ Lỗi Admin checkout: {e}")

        if conn:
            conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        if conn:
            conn.close()
# =====================================================
# START INITIALIZATION & CRASH RECOVERY
# =====================================================
client.on_message = on_message
client.subscribe("parking/#")
log("➡ Subscribed parking/#")

# =====================================================
# 1. LOAD SLOT STATUS FROM DB
# =====================================================
conn = None

try:
    conn = get_db_connection()

    with conn.cursor() as cur:
        cur.execute("SELECT Area, SlotCode, Status FROM parkingslot")
        rows = cur.fetchall()

    with state_lock:
        for row in rows:
            key = f"{row['Area']}{row['SlotCode']}"
            slotStatus[key] = "O" if row["Status"] == 1 else "X"

    log("📊 Đồng bộ trạng thái ban đầu từ DB thành công")

except Exception as e:
    log(f"⚠ Không thể lấy trạng thái ban đầu từ DB: {e}")

finally:
    if conn:
        conn.close()

# =====================================================
# 2. RESTORE EXIT CONTEXT (CRASH RECOVERY)
# =====================================================
log("🔄 Đang quét dữ liệu khôi phục (Crash Recovery)...")

try:
    saved_exit_ctx = load_cache("currentExitContext")

    if saved_exit_ctx:
        with currentExitLock:
            currentExitContext = saved_exit_ctx

        log(f"♻ [Hồi sinh] Xe đang chờ lối RA: RFID {saved_exit_ctx.get('rfid')}")

except Exception as e:
    log(f"⚠ Lỗi restore exit context: {e}")

# =====================================================
# 3. RESTORE ENTRY CONTEXT
# =====================================================
try:
    saved_pending_entry = load_cache("pendingEntry")

    if saved_pending_entry:
        with state_lock:
            pendingEntry = saved_pending_entry

        log(f"♻ [Hồi sinh] Xe đang chờ lối VÀO: RFID {saved_pending_entry.get('rfid')}")

except Exception as e:
    log(f"⚠ Lỗi restore entry context: {e}")
# =====================================================
# HTTP REALTIME HARDWARE SYNC
# =====================================================

# =====================================================
# HTTP REALTIME HARDWARE SYNC - SAFE STARTUP VERSION
# =====================================================

import threading
import time
import logging

# =====================================================
# MQTT START
# =====================================================
client.loop_start()

# =====================================================
# HEARTBEAT THREAD (SAFE)
# =====================================================
threading.Thread(
    target=send_web_heartbeat,
    args=(client,),
    daemon=True
).start()

# =====================================================
# FLASK SERVER THREAD (IMPORTANT: daemon=False)
# =====================================================
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def run_flask():
    app.run(
        host='0.0.0.0',
        port=5001,
        threaded=True,
        use_reloader=False,
        debug=False
    )

flask_thread = threading.Thread(
    target=run_flask,
    daemon=False   # ❗ QUAN TRỌNG: KHÔNG ĐƯỢC DAEMON
)
flask_thread.start()

log("🌐 Flask Web Stream started on http://0.0.0.0:5001/video_feed_entry and /video_feed_exit")

# =====================================================
# MAIN LOOP (SAFE + NO CRASH EXIT)
# =====================================================
def main_loop():
    while True:
        try:
            check_paid_and_open()
        except Exception as e:
            log(f"❌ MAIN LOOP ERROR: {e}")

        time.sleep(2)

threading.Thread(
    target=main_loop,
    daemon=False   # ❗ giữ process sống
).start()

# =====================================================
# PROCESS ANCHOR (GIỮ SYSTEM KHÔNG TỰ EXIT)
# =====================================================
try:
    while True:
        time.sleep(60)

except KeyboardInterrupt:
    log("🛑 KeyboardInterrupt")

finally:
    log("📷 Releasing camera")

    try:
        entry_camera.release()
    except:
        pass

    try:
        exit_camera.release()
    except:
        pass

    try:
        if _db_connection:
            _db_connection.close()
    except:
        pass

    log("👋 Shutdown complete")