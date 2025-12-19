import time
import json
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime
import re

from plate_scanner import scan_plate

# =====================================================
# LOG
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
# MQTT
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
pendingEntry = None   # chỉ để ưu tiên, KHÔNG bắt buộc

# =====================================================
# MAIN HANDLER
# =====================================================
def on_message(client, userdata, msg):
    global pendingEntry

    topic = msg.topic
    payload = msg.payload.decode().strip()
    log(f"📩 [{topic}] {payload}")

    try:
        # =================================================
        # IR SENSOR
        # =================================================
        if topic == "parking/gate/entry/ir":
            irStatus["ENTRY"] = payload
            return

        if topic == "parking/gate/exit/ir":
            irStatus["EXIT"] = payload
            return

        # =================================================
        # SLOT STATUS  (DEMO MODE)
        # O = Occupied, X = Empty
        # =================================================
        m = re.match(r"^parking/slot/([A-Z])(\d+)/status$", topic)
        if m:
            area = m.group(1)
            slotCode = m.group(2)
            status = payload

            log(f"ℹ Slot {area}{slotCode} status={status}")

            # ---------- KHI SLOT BỊ CHIẾM ----------
            if status == "O":
                # 1️⃣ ƯU TIÊN pendingEntry (xe vừa vào)
                if pendingEntry:
                    rfid = pendingEntry["rfid"]
                    log(f"➡ Assign slot using pendingEntry RFID={rfid}")
                else:
                    # 2️⃣ FALLBACK: lấy xe CHƯA RA gần nhất
                    with db.cursor() as cur:
                        cur.execute("""
                            SELECT RFID FROM parkinghistory
                            WHERE TimeOut IS NULL
                            ORDER BY TimeIn DESC
                            LIMIT 1
                        """)
                        row = cur.fetchone()

                    if not row:
                        log("⚠ No active vehicle to assign slot")
                        return

                    rfid = row["RFID"]
                    log(f"➡ Fallback assign slot to RFID={rfid}")

                # LẤY SlotID
                with db.cursor() as cur:
                    cur.execute("""
                        SELECT SlotID FROM parkingslot
                        WHERE Area=%s AND SlotCode=%s
                        LIMIT 1
                    """, (area, slotCode))
                    slotRow = cur.fetchone()

                if not slotRow:
                    log("❌ Slot not found in DB")
                    return

                slotId = slotRow["SlotID"]

                with db.cursor() as cur:
                    # GÁN SLOT CHO PARKINGHISTORY
                    cur.execute("""
                        UPDATE parkinghistory
                        SET SlotID=%s
                        WHERE RFID=%s AND TimeOut IS NULL
                        ORDER BY HistoryID DESC
                        LIMIT 1
                    """, (slotId, rfid))

                    # UPDATE PARKINGSLOT
                    cur.execute("""
                        UPDATE parkingslot
                        SET Status=0, CurrentRFID=%s
                        WHERE SlotID=%s
                    """, (rfid, slotId))

                pendingEntry = None
                log(f"✅ Slot {area}{slotCode} assigned to RFID {rfid}")
                return

            # ---------- KHI SLOT TRỐNG ----------
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
            log("⚠ Invalid RFID format")
            return

        gateType = m.group(1)
        rfid = m.group(2).strip()

        if irStatus.get(gateType) != "O":
            log("⛔ No vehicle at gate")
            return

        # =================================================
        # RFID CHECK
        # =================================================
        with db.cursor() as cur:
            cur.execute("SELECT 1 FROM rfidcard WHERE RFID=%s", (rfid,))
            if not cur.fetchone():
                client.publish("parking/rfid/auth", f"{rfid}:no")
                log("❌ RFID invalid")
                return

        client.publish("parking/rfid/auth", f"{rfid}:yes")
        log("✅ RFID valid")

        # =================================================
        # ENTRY
        # =================================================
        if gateType == "ENTRY":
            # CHECK FULL
            with db.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS free FROM parkingslot WHERE Status=0")
                if cur.fetchone()["free"] == 0:
                    log("⛔ PARKING FULL")
                    client.publish("parking/gate/cmd", "DENY_ENTRY")
                    return

            # CHECK INSIDE
            with db.cursor() as cur:
                cur.execute("""
                    SELECT 1 FROM parkinghistory
                    WHERE RFID=%s AND TimeOut IS NULL
                    LIMIT 1
                """, (rfid,))
                if cur.fetchone():
                    log("⛔ RFID already inside")
                    return

            # AI ENTRY
            try:
                img_entry, _, plate_entry = scan_plate()
                if plate_entry == "unknown":
                    plate_entry = None
                    img_entry = None
            except:
                img_entry = None
                plate_entry = None

            client.publish("parking/gate/cmd", "OPEN_ENTRY")
            log("🚪 OPEN_ENTRY")

            pendingEntry = {"rfid": rfid, "time": time.time()}

            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO parkinghistory
                    (RFID, TimeIn, ImageFullEntry, PlateNumberEntry)
                    VALUES (%s, NOW(), %s, %s)
                """, (rfid, img_entry, plate_entry))

            log(f"✅ ENTRY saved | Plate={plate_entry}")
            return

        # =================================================
        # EXIT
        # =================================================
        if gateType == "EXIT":
            with db.cursor() as cur:
                cur.execute("""
                    SELECT TimeIn, PlateNumberEntry
                    FROM parkinghistory
                    WHERE RFID=%s AND TimeOut IS NULL
                    ORDER BY HistoryID DESC
                    LIMIT 1
                """, (rfid,))
                entry = cur.fetchone()

            if not entry:
                log("⛔ No active entry")
                return

            entry_plate = norm_plate(entry["PlateNumberEntry"])

            plate_match = False
            try:
                img_exit, _, plate_exit = scan_plate()
                plate_exit_n = norm_plate(plate_exit)
                if entry_plate and plate_exit_n == entry_plate:
                    plate_match = True
            except:
                img_exit = None
                plate_exit = None

            if not plate_match:
                log("⛔ Plate mismatch")
                client.publish("parking/gate/cmd", "DENY_EXIT")
                return

            client.publish("parking/gate/cmd", "OPEN_EXIT")
            log("🚪 OPEN_EXIT")

            with db.cursor() as cur:
                cur.execute("""
                    UPDATE parkinghistory
                    SET
                        TimeOut = NOW(),
                        Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()),
                        Fee = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) * 10,
                        ImageFullExit = %s,
                        PlateNumberExit = %s
                    WHERE RFID=%s AND TimeOut IS NULL
                    ORDER BY HistoryID DESC
                    LIMIT 1
                """, (img_exit, plate_exit, rfid))

            # FREE SLOT (NẾU CÓ)
            with db.cursor() as cur:
                cur.execute("""
                    UPDATE parkingslot
                    SET Status=0, CurrentRFID=NULL
                    WHERE CurrentRFID=%s
                """, (rfid,))

            log("✅ EXIT saved & slot freed")
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
