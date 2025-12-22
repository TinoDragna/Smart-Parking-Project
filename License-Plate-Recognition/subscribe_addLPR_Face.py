import time
import threading
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime
import re

from plate_scanner import scan_plate
from face_detect_deepface_faster import check_in_face, check_out_face

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
# RFID STATE CHECK
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
# GATE LOG
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
pendingEntry = None

# =====================================================
# CAMERA LOCK
# =====================================================
camera_lock = threading.Lock()

def safe_scan_plate():
    print("LPR start")
    with camera_lock:
        print("YYYYY")
        return scan_plate()

def safe_face_checkin():
    print("Face start in")
    with camera_lock:
        return check_in_face()

def safe_face_checkout():
    print("Face start out")
    with camera_lock:
        return check_out_face()

# =====================================================
# ENTRY WORKER
# =====================================================
def entry_worker(rfid):
    global pendingEntry

    img_entry, _, plate_entry = safe_scan_plate()
    if not plate_entry:
        write_log("ENTRY", "LPR_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_ENTRY")
        return

    face_res = safe_face_checkin()
    if not face_res or not face_res["success"]:
        write_log("ENTRY", "FACE_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_ENTRY")
        return

    face_path = face_res["image_path"]

    client.publish("parking/gate/cmd", "OPEN_ENTRY")
    write_log("ENTRY", "OPEN", rfid)

    pendingEntry = {"rfid": rfid, "time": time.time()}

    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO parkinghistory
            (RFID, TimeIn, ImageFullEntry, PlateNumberEntry, FaceImageEntry)
            VALUES (%s, NOW(), %s, %s, %s)
        """, (rfid, img_entry, plate_entry, face_path))

# =====================================================
# EXIT WORKER
# =====================================================
def exit_worker(rfid, entry_plate):
    global pendingEntry

    img_exit, _, plate_exit = safe_scan_plate()
    if not plate_exit:
        write_log("EXIT", "LPR_FAIL", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        return

    if entry_plate and norm_plate(plate_exit) != entry_plate:
        write_log("EXIT", "LPR_MISMATCH", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        return

    face_res = safe_face_checkout()
    if not face_res or not face_res["success"]:
        write_log("EXIT", "FACE_MISMATCH", rfid)
        client.publish("parking/gate/cmd", "DENY_EXIT")
        return

    face_path = face_res["image_path"]

    client.publish("parking/gate/cmd", "OPEN_EXIT")
    write_log("EXIT", "OPEN", rfid)

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

    with db.cursor() as cur:
        cur.execute("""
            UPDATE parkingslot
            SET Status=0, CurrentRFID=NULL
            WHERE CurrentRFID=%s
        """, (rfid,))

    pendingEntry = None

# =====================================================
# MQTT MESSAGE HANDLER
# =====================================================
def on_message(client, userdata, msg):
    global pendingEntry

    topic = msg.topic
    payload = msg.payload.decode().strip()
    log(f"📩 [{topic}] {payload}")

    try:
        if topic == "parking/gate/entry/ir":
            irStatus["ENTRY"] = payload
            return

        if topic == "parking/gate/exit/ir":
            irStatus["EXIT"] = payload
            return

        m = re.match(r"^parking/slot/([A-Z])(\d+)/status$", topic)
        if m:
            area, slotCode = m.group(1), m.group(2)
            status = payload

            if status == "O":
                rfid = pendingEntry["rfid"] if pendingEntry else None
                if not rfid:
                    return

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
                return

            if status == "X":
                with db.cursor() as cur:
                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=1, CurrentRFID=NULL
                        WHERE Area=%s AND SlotCode=%s
                    """, (area, slotCode))
                return

        if topic != "parking/rfid":
            return

        m = re.match(r"^(ENTRY|EXIT):(.+)$", payload)
        if not m:
            return

        gateType, rfid = m.group(1), m.group(2).strip()
        if irStatus.get(gateType) != "O":
            return

        with db.cursor() as cur:
            cur.execute("SELECT 1 FROM rfidcard WHERE RFID=%s", (rfid,))
            if not cur.fetchone():
                write_log(gateType, "RFID_INVALID", rfid)
                client.publish("parking/gate/cmd", f"DENY_{gateType}")
                return

        if gateType == "ENTRY":
            if rfid_is_inside(rfid):
                write_log("ENTRY", "ALREADY_INSIDE", rfid)
                client.publish("parking/gate/cmd", "DENY_ENTRY")
                return

            threading.Thread(
                target=entry_worker,
                args=(rfid,),
                daemon=True
            ).start()
            return

        if gateType == "EXIT":
            if not rfid_is_inside(rfid):
                write_log("EXIT", "NO_ACTIVE_ENTRY", rfid)
                client.publish("parking/gate/cmd", "DENY_EXIT")
                return

            with db.cursor() as cur:
                cur.execute("""
                    SELECT PlateNumberEntry
                    FROM parkinghistory
                    WHERE RFID=%s AND TimeOut IS NULL
                    ORDER BY HistoryID DESC
                    LIMIT 1
                """, (rfid,))
                row = cur.fetchone()

            threading.Thread(
                target=exit_worker,
                args=(rfid, norm_plate(row["PlateNumberEntry"])),
                daemon=True
            ).start()
            return

    except Exception as e:
        log(f"❌ ERROR: {e}")

def on_disconnect(client, userdata, msg):
    print("disconnect")
    

# =====================================================
# START
# =====================================================
client.on_message = on_message 
client.subscribe("parking/#")
log("➡ Subscribed parking/#")
client.on_disconnect = on_disconnect
client.loop_forever()
