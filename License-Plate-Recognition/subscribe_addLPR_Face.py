import time
import threading
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime
import re

from plate_scanner import scan_plate
from face_detect_deepface_faster import check_in_face, check_out_face

# =====================================================
# LOG (console)
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
# WRITE GATE LOG  (GIỮ ĐÚNG DB CỦA BẠN)
# =====================================================
def write_log(gate, action, triggered_by):
    try:
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO gatelog (GateType, Action, Time, TriggeredBy)
                VALUES (%s, %s, NOW(), %s)
            """, (gate, action, triggered_by))
    except Exception as e:
        log(f"⚠ LOG FAILED: {e}")

# =====================================================
# MQTT
# =====================================================
MQTT_SERVER = "172.16.2.4"
MQTT_PORT = 1883

client_id = "py_control_" + str(int(time.time()))
client = mqtt.Client(client_id=client_id)
client.connect(MQTT_SERVER, MQTT_PORT, 60)
log("✅ MQTT connected")

# =====================================================
# GLOBAL STATE (GIỮ NGUYÊN)
# =====================================================
irStatus = {"ENTRY": None, "EXIT": None}
pendingEntry = None   # ❗ GIỮ

# =====================================================
# ASYNC FACE CHECK-IN  (CHỈ CHẠY FACE)
# =====================================================
def run_face_checkin_async(rfid, img_entry, plate_entry):
    global pendingEntry

    log("🧠 FACE CHECK-IN started")

    face_res = check_in_face()
    if not face_res or not face_res["success"]:
        write_log("ENTRY", "FACE_CHECKIN_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_ENTRY")
        log("⛔ FACE CHECK-IN FAIL")
        return

    face_path = face_res["image_path"]

    client.publish("parking/gate/cmd", "OPEN_ENTRY")
    write_log("ENTRY", "OPEN", rfid)
    log("🚪 OPEN_ENTRY")

    pendingEntry = {"rfid": rfid, "time": time.time()}

    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO parkinghistory
            (RFID, TimeIn, ImageFullEntry, PlateNumberEntry, FaceImageEntry)
            VALUES (%s, NOW(), %s, %s, %s)
        """, (rfid, img_entry, plate_entry, face_path))

    log("✅ ENTRY saved (GIỮ LOGIC CŨ + FACE)")

# =====================================================
# ASYNC FACE CHECK-OUT
# =====================================================
def run_face_checkout_async(rfid, img_exit, plate_exit):
    log("🧠 FACE CHECK-OUT started")

    face_res = check_out_face()
    if not face_res or not face_res["success"]:
        client.publish("parking/gate/cmd", "DENY_EXIT")
        write_log("EXIT", "FACE_MISMATCH", rfid)
        log("⛔ FACE NOT MATCHED")
        return

    face_path = face_res["image_path"]

    client.publish("parking/gate/cmd", "OPEN_EXIT")
    write_log("EXIT", "OPEN", rfid)
    log("🚪 OPEN_EXIT")

    with db.cursor() as cur:
        cur.execute("""
            UPDATE parkinghistory
            SET
                TimeOut = NOW(),
                Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()),
                Fee = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) * 10,
                ImageFullExit = %s,
                PlateNumberExit = %s,
                FaceImageExit = %s
            WHERE RFID=%s AND TimeOut IS NULL
            ORDER BY HistoryID DESC
            LIMIT 1
        """, (img_exit, plate_exit, face_path, rfid))

    # ❗ GIỮ LOGIC FREE SLOT
    with db.cursor() as cur:
        cur.execute("""
            UPDATE parkingslot
            SET Status=0, CurrentRFID=NULL
            WHERE CurrentRFID=%s
        """, (rfid,))

    log("✅ EXIT saved & slot freed (GIỮ LOGIC CŨ)")

# =====================================================
# MAIN HANDLER (GIỮ CẤU TRÚC CŨ)
# =====================================================
def on_message(client, userdata, msg):
    global pendingEntry

    topic = msg.topic
    payload = msg.payload.decode().strip()
    log(f"📩 [{topic}] {payload}")

    try:
        # =================================================
        # IR SENSOR  (GIỮ)
        # =================================================
        if topic == "parking/gate/entry/ir":
            irStatus["ENTRY"] = payload
            return

        if topic == "parking/gate/exit/ir":
            irStatus["EXIT"] = payload
            return

        # =================================================
        # SLOT STATUS  (GIỮ NGUYÊN)
        # =================================================
        m = re.match(r"^parking/slot/([A-Z])(\d+)/status$", topic)
        if m:
            area = m.group(1)
            slotCode = m.group(2)
            status = payload

            log(f"ℹ Slot {area}{slotCode} status={status}")

            # ---------- SLOT OCCUPIED ----------
            if status == "O":
                if pendingEntry:
                    rfid = pendingEntry["rfid"]
                else:
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
                        SET Status=0, CurrentRFID=%s
                        WHERE SlotID=%s
                    """, (rfid, slotId))

                pendingEntry = None
                log(f"✅ Slot {area}{slotCode} assigned to RFID {rfid}")
                return

            # ---------- SLOT EMPTY ----------
            if status == "X":
                with db.cursor() as cur:
                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=1, CurrentRFID=NULL
                        WHERE Area=%s AND SlotCode=%s
                    """, (area, slotCode))
                log(f"ℹ Slot {area}{slotCode} marked EMPTY")
                return

        # =================================================
        # RFID
        # =================================================
        if topic != "parking/rfid":
            return

        m = re.match(r"^(ENTRY|EXIT):(.+)$", payload)
        if not m:
            return

        gateType = m.group(1)
        rfid = m.group(2).strip()

        if irStatus.get(gateType) != "O":
            return

        # =================================================
        # RFID CHECK  (GIỮ)
        # =================================================
        with db.cursor() as cur:
            cur.execute("SELECT 1 FROM rfidcard WHERE RFID=%s", (rfid,))
            if not cur.fetchone():
                write_log(gateType, "RFID_INVALID", rfid)
                return

        # =================================================
        # ENTRY  (GIỮ + CHÈN LPR + FACE)
        # =================================================
        if gateType == "ENTRY":

            # CHECK FULL  (GIỮ)
            with db.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS free FROM parkingslot WHERE Status=0")
                if cur.fetchone()["free"] == 0:
                    client.publish("parking/gate/cmd", "DENY_ENTRY")
                    write_log("ENTRY", "PARKING_FULL", rfid)
                    return

            # CHECK INSIDE  (GIỮ)
            with db.cursor() as cur:
                cur.execute("""
                    SELECT 1 FROM parkinghistory
                    WHERE RFID=%s AND TimeOut IS NULL
                    LIMIT 1
                """, (rfid,))
                if cur.fetchone():
                    write_log("ENTRY", "RFID_ALREADY_INSIDE", rfid)
                    return

            # LPR ENTRY  (GIỮ)
            try:
                img_entry, _, plate_entry = scan_plate()
                if plate_entry == "unknown":
                    plate_entry = None
                    img_entry = None
            except:
                client.publish("parking/gate/cmd", "DENY_ENTRY")
                write_log("ENTRY", "LPR_FAIL", rfid)
                return

            # 👉 CHÈN FACE ASYNC
            threading.Thread(
                target=run_face_checkin_async,
                args=(rfid, img_entry, plate_entry),
                daemon=True
            ).start()

            log("🧠 FACE CHECK-IN THREAD STARTED")
            return

        # =================================================
        # EXIT  (GIỮ + CHÈN LPR + FACE)
        # =================================================
        if gateType == "EXIT":

            with db.cursor() as cur:
                cur.execute("""
                    SELECT PlateNumberEntry
                    FROM parkinghistory
                    WHERE RFID=%s AND TimeOut IS NULL
                    ORDER BY HistoryID DESC
                    LIMIT 1
                """, (rfid,))
                entry = cur.fetchone()

            if not entry:
                write_log("EXIT", "NO_ACTIVE_ENTRY", rfid)
                return

            entry_plate = norm_plate(entry["PlateNumberEntry"])

            # LPR EXIT  (GIỮ)
            try:
                img_exit, _, plate_exit = scan_plate()
                if not plate_exit or plate_exit == "unknown":
                    raise Exception("LPR unknown")
            except:
                client.publish("parking/gate/cmd", "DENY_EXIT")
                write_log("EXIT", "LPR_FAIL", rfid)
                return

            if entry_plate and norm_plate(plate_exit) != entry_plate:
                client.publish("parking/gate/cmd", "DENY_EXIT")
                write_log("EXIT", "LPR_MISMATCH", rfid)
                return

            # 👉 CHÈN FACE ASYNC
            threading.Thread(
                target=run_face_checkout_async,
                args=(rfid, img_exit, plate_exit),
                daemon=True
            ).start()

            log("🧠 FACE CHECK-OUT THREAD STARTED")
            return

    except Exception as e:
        log(f"❌ ERROR: {e}")

# =====================================================
# START
# =====================================================
client.on_message = on_message
client.subscribe("parking/#")
log("➡ Subscribed parking/#")
client.loop_forever()
