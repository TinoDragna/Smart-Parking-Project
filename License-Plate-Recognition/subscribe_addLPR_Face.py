import faulthandler
faulthandler.enable()

import json
import time
import threading
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime
import re

from plate_scanner import scan_plate
from face_detect_deepface_faster import check_in_face, check_out_face
from camera import camera


# O: Occupied, X: Empty
# 1: Occupied, 0: Empty
# =====================================================
# CONSOLE LOG
# =====================================================
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

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
pendingEntry = None   # RFID vừa vào, dùng để gán slot chính xác

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
    img_entry, _, plate_entry = safe_scan_plate()
    if not plate_entry:
        write_log("ENTRY", "LPR_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_ENTRY")
        log("⛔ ENTRY LPR FAIL")
        return

    # --- FACE CHECK-IN ---
    face_res = safe_face_checkin()
    if not face_res or not face_res["success"]:
        write_log("ENTRY", "FACE_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_ENTRY")
        log("⛔ ENTRY FACE FAIL")
        return

    face_path = face_res["image_path"]

    # --- OPEN GATE ---
    client.publish("parking/gate/cmd", "OPEN_ENTRY")
    write_log("ENTRY", "OPEN", rfid)
    log("🚪 OPEN_ENTRY")

    pendingEntry = {"rfid": rfid, "time": time.time()}

    # --- LƯU LỊCH SỬ VÀO ---
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO parkinghistory
            (RFID, TimeIn, ImageFullEntry, PlateNumberEntry, FaceImageEntry)
            VALUES (%s, NOW(), %s, %s, %s)
        """, (rfid, img_entry, plate_entry, face_path))

    log("✅ ENTRY SAVED")

# =====================================================
# EXIT WORKER: LPR → FACE → OPEN EXIT
# =====================================================
def exit_worker(rfid, entry_plate, face_entry_path):
    # --- LPR EXIT ---
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
    face_res = safe_face_checkout(face_entry_path)
    if not face_res or not face_res["success"]:
        write_log("EXIT", "FACE_MISMATCH", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        log("⛔ EXIT FACE FAIL")
        return

    face_path = face_res["image_path"]

    # # --- OPEN GATE --- Không open vì chưa trả tiền
    # client.publish("parking/gate/cmd", "OPEN_EXIT")
    # write_log("EXIT", "OPEN", rfid)
    # log("🚪 OPEN_EXIT")

    # --- CẬP NHẬT LỊCH SỬ RA ---
    # with db.cursor() as cur:
    #     cur.execute("""
    #         UPDATE parkinghistory
    #         SET
    #             TimeOut = NOW(),
    #             Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()),
    #             Fee = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()),
    #             ImageFullExit = %s,
    #             PlateNumberExit = %s,
    #             FaceImageExit = %s
    #         WHERE RFID=%s AND TimeOut IS NULL
    #         ORDER BY HistoryID DESC
    #         LIMIT 1
    #     """, (img_exit, plate_exit, face_path, rfid))

    with db.cursor() as cur:
        cur.execute("""
            UPDATE parkinghistory
            SET
                ImageFullExit = %s,
                PlateNumberExit = %s,
                FaceImageExit = %s
            WHERE RFID=%s AND TimeOut IS NULL
            ORDER BY HistoryID DESC
            LIMIT 1
        """, (img_exit, plate_exit, face_path, rfid))

    # # --- GIẢI PHÓNG SLOT ---
    # with db.cursor() as cur:
    #     cur.execute("""
    #         UPDATE parkingslot
    #         SET Status=0, CurrentRFID=NULL
    #         WHERE CurrentRFID=%s
    #     """, (rfid,))

    # log("✅ EXIT SAVED & SLOT FREED")

    # --- TÍNH PHÍ ---
    with db.cursor() as cur:
        cur.execute("""
            SELECT TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) AS minutes
            FROM parkinghistory
            WHERE RFID=%s AND TimeOut IS NULL
            ORDER BY HistoryID DESC
            LIMIT 1
        """, (rfid,))
        m = cur.fetchone()

    minutes = m["minutes"] if m and m["minutes"] else 0
    hours = (minutes + 59) // 60
    fee = hours * 5000

    # --- TRÁNH DUPLICATE PAYMENT ---
    with db.cursor() as cur:
        cur.execute("""
            SELECT PaymentID FROM payments
            WHERE RFID=%s AND Status='pending'
            LIMIT 1
        """, (rfid,))
        if cur.fetchone():
            log(f"ℹ PAYMENT already exists for {rfid}")
            return

    # --- INSERT PAYMENT ---
    with db.cursor() as cur:
        cur.execute("""
            SELECT HistoryID FROM parkinghistory
            WHERE RFID=%s AND TimeOut IS NULL
            ORDER BY HistoryID DESC LIMIT 1
        """, (rfid,))
        history = cur.fetchone()

        cur.execute("""
            INSERT INTO payments (RFID, HistoryID, Amount)
            VALUES (%s, %s, %s)
        """, (rfid, history["HistoryID"], fee))

        paymentId = cur.lastrowid

    log(f"💳 PAYMENT CREATED: {paymentId} | RFID {rfid} | Fee {fee}")

# =====================================================
# PAYMENT CHECK (DB → MQTT)
# =====================================================
def check_paid_and_open():
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT PaymentID, RFID
                FROM payments
                WHERE Status='paid' AND Notified=0
                ORDER BY PaymentID ASC
                LIMIT 1
            """)
            row = cur.fetchone()

        if not row:
            return

        paymentId = row["PaymentID"]
        rfid = row["RFID"]

        log(f"💰 Payment detected: {paymentId} | RFID {rfid}")

        # ===== OPEN GATE =====
        client.publish("parking/gate/cmd", "OPEN_EXIT")
        log("🚪 OPEN_EXIT (from payment)")

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

                with db.cursor() as cur:

                    # ===== 1. TÌM RFID ĐANG Ở CỔNG =====
                    cur.execute("""
                        SELECT CurrentRFID
                        FROM parkingslot
                        WHERE CurrentRFID IS NOT NULL
                        LIMIT 1
                    """)
                    row = cur.fetchone()

                    if not row:
                        log("⚠ No vehicle at exit")
                        return

                    rfid_exit = row["CurrentRFID"]

                    # ===== 2. UPDATE TIMEOUT =====
                    cur.execute("""
                        UPDATE parkinghistory
                        SET TimeOut = NOW(),
                            Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW())
                        WHERE RFID=%s AND TimeOut IS NULL
                        ORDER BY HistoryID DESC LIMIT 1
                    """, (rfid_exit,))

                    # ===== 3. LẤY PAYMENT ĐÃ TRẢ =====
                    cur.execute("""
                        SELECT Amount
                        FROM payments
                        WHERE RFID=%s AND Status='paid'
                        ORDER BY PaymentID DESC LIMIT 1
                    """, (rfid_exit,))
                    p = cur.fetchone()

                    if p:
                        # ===== 4. COPY FEE =====
                        cur.execute("""
                            UPDATE parkinghistory
                            SET Fee=%s
                            WHERE RFID=%s AND TimeOut IS NOT NULL
                            ORDER BY HistoryID DESC LIMIT 1
                        """, (p["Amount"], rfid_exit))

                    # ===== 5. FREE SLOT =====
                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=0, CurrentRFID=NULL
                        WHERE CurrentRFID=%s
                    """, (rfid_exit,))

                log(f"🚗 EXIT COMPLETE | RFID {rfid_exit}")

            return
        # -------- SLOT STATUS --------
        m = re.match(r"^parking/slot/([A-Z])(\d+)/status$", topic)
        if m:
            area, slotCode = m.group(1), m.group(2)
            status = payload

            # Slot bị chiếm → gán cho xe vừa vào
            if status == "O":
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
                            return
                        rfid = row["RFID"]

                with db.cursor() as cur:
                    cur.execute("""
                        SELECT SlotID FROM parkingslot
                        WHERE Area=%s AND SlotCode=%s
                        LIMIT 1
                    """, (area, slotCode))
                    slotId = cur.fetchone()["SlotID"]

                    cur.execute("""
                        UPDATE parkinghistory
                        SET SlotID=%s
                        WHERE RFID=%s AND TimeOut IS NULL
                        ORDER BY HistoryID DESC
                        LIMIT 1
                    """, (slotId, rfid))

                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=1, CurrentRFID=%s
                        WHERE SlotID=%s
                    """, (rfid, slotId))

                pendingEntry = None
                log(f"✅ SLOT {area}{slotCode} ASSIGNED TO {rfid}")
                return

            # Slot trống
            if status == "X":
                with db.cursor() as cur:
                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=0, CurrentRFID=NULL
                        WHERE Area=%s AND SlotCode=%s
                    """, (area, slotCode))
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
                    SELECT PlateNumberEntry, FaceImageEntry
                    FROM parkinghistory
                    WHERE RFID=%s AND TimeOut IS NULL
                    ORDER BY HistoryID DESC
                    LIMIT 1
                """, (rfid,))
                row = cur.fetchone()

            if not row:
                write_log("EXIT", "NO_ACTIVE_ENTRY", rfid)
                return

            threading.Thread(
                target=exit_worker,
                args=(rfid, norm_plate(row["PlateNumberEntry"]), row["FaceImageEntry"]),
                daemon=True
            ).start()
            return

    except Exception as e:
        log(f"❌ ERROR: {e}")
 
# =====================================================
# START
# =====================================================
client.on_message = on_message
client.subscribe("parking/#")
log("➡ Subscribed parking/#")

client.loop_start()

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
