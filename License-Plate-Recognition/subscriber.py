import time
import json
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime

# ================================
# LOG FUNCTION
# ================================
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

# ================================
# DB CONNECTION
# ================================
try:
    db = pymysql.connect(
        host="localhost",
        user="smartparking",
        password="cyber@2025",
        database="smart_parking",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    log("✅ DB connected")
except Exception as e:
    log(f"❌ DB connect failed: {e}")
    exit(1)


# ================================
# MQTT SETUP
# ================================
MQTT_SERVER = "172.16.2.4"
MQTT_PORT = 1883

client_id = "py_control_" + str(int(time.time()))

client = mqtt.Client(client_id=client_id)

try:
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    log(f"✅ MQTT connected to {MQTT_SERVER}:{MQTT_PORT}")
except Exception as e:
    log(f"❌ Cannot connect to MQTT Broker: {e}")
    exit(1)


# ================================
# GLOBAL STATE
# ================================
irStatus = {'ENTRY': None, 'EXIT': None}
slotStatus = {}
pendingEntry = None


# ================================
# MAIN MESSAGE HANDLER
# ================================
def on_message(client, userdata, msg):
    global irStatus, slotStatus, pendingEntry

    topic = msg.topic
    payload = msg.payload.decode()
    log(f"📩 Received [{topic}]: {payload}")

    try:
        # ==========================================
        # 1. IR STATUS UPDATE
        # ==========================================
        if topic == "parking/gate/entry/ir":
            irStatus['ENTRY'] = payload.strip()
            log(f"ℹ Entry IR status: {irStatus['ENTRY']}")
            return

        if topic == "parking/gate/exit/ir":
            irStatus['EXIT'] = payload.strip()
            log(f"ℹ Exit IR status: {irStatus['EXIT']}")
            return

        # ==========================================
        # 2. SLOT STATUS UPDATE
        # ==========================================
        import re
        m = re.match(r"^parking/slot/([A-Z])(\d+)/status$", topic)
        if m:
            area = m.group(1)
            slotCode = m.group(2)

            data = json.loads(payload)
            if "status" in data:
                slotStatus[f"{area}{slotCode}"] = data["status"]
                log(f"ℹ Slot {area}{slotCode} updated to {data['status']}")
            return

        # ==========================================
        # 3. RFID READER
        # ==========================================
        if topic == "parking/rfid":
            m = re.match(r"^(ENTRY|EXIT):(.+)$", payload)
            if not m:
                log(f"⚠ Invalid RFID format: {payload}")
                return

            gateType = m.group(1)
            rfid = m.group(2).strip()

            # Check IR first
            if irStatus.get(gateType) != "O":
                log(f"⛔ IR {gateType} no vehicle (status={irStatus.get(gateType)}), ignore RFID {rfid}")
                return

            # DB check
            with db.cursor() as cur:
                cur.execute("SELECT RFID FROM rfidcard WHERE RFID=%s", (rfid,))
                exists = cur.fetchone()

            if exists:   # VALID RFID
                authMsg = f"{rfid}:yes"
                client.publish("parking/rfid/auth", authMsg)
                log(f"✅ RFID {rfid} hợp lệ → {authMsg}")

                # ===== ENTRY =====
                if gateType == "ENTRY":
                    with db.cursor() as cur:
                        cur.execute("SELECT 1 FROM parkinghistory WHERE RFID=%s AND TimeOut IS NULL LIMIT 1", (rfid,))
                        inside = cur.fetchone()

                    if inside:
                        log(f"⛔ RFID {rfid} đã ở trong bãi → không mở cổng")
                        return

                    client.publish("parking/gate/cmd", "OPEN_ENTRY")
                    log("🚪 Mở cổng vào")

                    pendingEntry = {"rfid": rfid, "time": time.time()}

                    with db.cursor() as cur:
                        cur.execute("""
                            INSERT INTO parkinghistory (RFID, SlotID, TimeIn)
                            VALUES (%s, NULL, NOW())
                        """, (rfid,))
                    log(f"✅ Thêm parkinghistory cho RFID {rfid} (ENTRY)")

                # ===== EXIT =====
                elif gateType == "EXIT":
                    with db.cursor() as cur:
                        cur.execute("SELECT 1 FROM parkinghistory WHERE RFID=%s AND TimeOut IS NULL", (rfid,))
                        inside = cur.fetchone()

                    if not inside:
                        log(f"⛔ RFID {rfid} không có xe trong bãi → không mở cổng ra")
                        return

                    client.publish("parking/gate/cmd", "OPEN_EXIT")
                    log("🚪 Mở cổng ra")

                    with db.cursor() as cur:
                        cur.execute("SELECT SlotID FROM parkingslot WHERE CurrentRFID=%s LIMIT 1", (rfid,))
                        slotRow = cur.fetchone()

                    if slotRow:
                        slotIdExit = slotRow["SlotID"]

                        with db.cursor() as cur:
                            cur.execute("""
                                UPDATE parkinghistory
                                SET TimeOut = NOW()
                                WHERE RFID=%s AND TimeOut IS NULL
                                ORDER BY HistoryID DESC LIMIT 1
                            """, (rfid,))

                            cur.execute("""
                                UPDATE parkinghistory
                                SET Duration = TIMESTAMPDIFF(MINUTE, TimeIn, TimeOut),
                                    Fee = TIMESTAMPDIFF(MINUTE, TimeIn, TimeOut) * 10
                                WHERE RFID=%s AND TimeOut IS NOT NULL
                                ORDER BY HistoryID DESC LIMIT 1
                            """, (rfid,))

                            cur.execute("UPDATE parkingslot SET Status=0, CurrentRFID=NULL WHERE SlotID=%s", (slotIdExit,))

                        log(f"🚗 RFID {rfid} rời SlotID {slotIdExit}, slot trống lại")

            else:  # INVALID RFID
                authMsg = f"{rfid}:no"
                client.publish("parking/rfid/auth", authMsg)
                log(f"❌ RFID {rfid} không hợp lệ → {authMsg}")
            return

        # ==========================================
        # 4. LOG SLOT CHANGE (for ENTRY)
        # ==========================================
        if topic == "parking/log":
            data = json.loads(payload)

            if data.get("event") == "slot_change" and "slot" in data and "status" in data:
                slotCode = data["slot"]  # e.g., B1
                status = data["status"]

                area = slotCode[0]
                slotNum = slotCode[1:]

                # Only if ENTRY pending
                if status == "X" and pendingEntry and (time.time() - pendingEntry["time"] <= 300):

                    with db.cursor() as cur:
                        cur.execute("SELECT SlotID FROM parkingslot WHERE Area=%s AND SlotCode=%s LIMIT 1",
                                    (area, slotNum))
                        slotRow = cur.fetchone()

                    if slotRow:
                        slotId = slotRow["SlotID"]

                        with db.cursor() as cur:
                            cur.execute("""
                                UPDATE parkinghistory
                                SET SlotID=%s
                                WHERE RFID=%s AND SlotID IS NULL
                                ORDER BY HistoryID DESC LIMIT 1
                            """, (slotId, pendingEntry["rfid"]))

                            cur.execute("""
                                UPDATE parkingslot
                                SET Status=1, CurrentRFID=%s
                                WHERE SlotID=%s
                            """, (pendingEntry["rfid"], slotId))

                        log(f"✅ Gán Slot {slotCode} cho RFID {pendingEntry['rfid']}")
                        pendingEntry = None
            return

    except Exception as e:
        log(f"❌ Error: {e}")


# ================================
# SUBSCRIBE & START LOOP
# ================================
client.on_message = on_message
client.subscribe("parking/#")
log("➡ Subscribed to parking/#")

client.loop_forever()
