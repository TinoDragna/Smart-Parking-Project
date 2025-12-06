import time
import json
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime

from plate_scanner import scan_plate

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
        # 3. RFID READER (AI INTEGRATION)
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

            if not exists:
                # INVALID RFID
                authMsg = f"{rfid}:no"
                client.publish("parking/rfid/auth", authMsg)
                log(f"❌ RFID {rfid} không hợp lệ → {authMsg}")
                return

            # ===== VALID RFID - Publish auth =====
            authMsg = f"{rfid}:yes"
            client.publish("parking/rfid/auth", authMsg)
            log(f"✅ RFID {rfid} hợp lệ → {authMsg}")

            # ===== ENTRY GATE =====
            if gateType == "ENTRY":
                with db.cursor() as cur:
                    cur.execute("SELECT 1 FROM parkinghistory WHERE RFID=%s AND TimeOut IS NULL LIMIT 1", (rfid,))
                    inside = cur.fetchone()

                if inside:
                    log(f"⛔ RFID {rfid} đã ở trong bãi → không mở cổng")
                    return

                # 🎯 CALL AI TO SCAN LICENSE PLATE
                log("🤖 Starting AI license plate recognition...")
                try:
                    full_crop, min_crop, plate_number = scan_plate()
                    
                    if plate_number and plate_number != "unknown":
                        log(f"✅ AI detected plate: {plate_number}")
                        log(f"📁 Saved image: {full_crop}")
                    else:
                        log("⚠️ AI could not detect plate, continuing anyway...")
                        plate_number = None
                        full_crop = None

                except Exception as e:
                    log(f"❌ AI scan failed: {e}")
                    plate_number = None
                    full_crop = None

                # Open gate
                client.publish("parking/gate/cmd", "OPEN_ENTRY")
                log("🚪 Mở cổng vào")

                pendingEntry = {"rfid": rfid, "time": time.time()}

                # Save ENTRY record with AI data
                with db.cursor() as cur:
                    cur.execute("""
                        INSERT INTO parkinghistory 
                        (RFID, SlotID, TimeIn, ImageFull, PlateNumber)
                        VALUES (%s, NULL, NOW(), %s, %s)
                    """, (rfid, full_crop, plate_number))
                
                log(f"✅ Lưu ENTRY: RFID={rfid}, Plate={plate_number}")

            # ===== EXIT GATE =====
            elif gateType == "EXIT":
                with db.cursor() as cur:
                    # Get entry data
                    cur.execute("""
                        SELECT TimeIn, PlateNumber, ImageFull
                        FROM parkinghistory 
                        WHERE RFID=%s AND TimeOut IS NULL
                        ORDER BY HistoryID DESC
                        LIMIT 1
                    """, (rfid,))
                    entry_record = cur.fetchone()

                if not entry_record:
                    log(f"⛔ RFID {rfid} không có xe trong bãi → không mở cổng ra")
                    return

                entry_time = entry_record['TimeIn']
                entry_plate = entry_record.get('PlateNumber')
                entry_image = entry_record.get('ImageFull')
                
                log(f"📋 Entry data: Plate={entry_plate}, Time={entry_time}")

                # 🎯 CALL AI TO SCAN LICENSE PLATE AT EXIT
                log("🤖 Starting AI license plate recognition at EXIT...")
                try:
                    image_full_exit, image_crop_exit, plate_number_exit = scan_plate()
                    
                    if plate_number_exit and plate_number_exit != "unknown":
                        log(f"✅ AI detected exit plate: {plate_number_exit}")
                        
                        # Compare plates
                        if entry_plate and plate_number_exit == entry_plate:
                            log("✅✅✅ Plate MATCH! Same vehicle confirmed ✅✅✅")
                        elif entry_plate:
                            log(f"⚠️⚠️⚠️ Plate MISMATCH! Entry: {entry_plate} vs Exit: {plate_number_exit} ⚠️⚠️⚠️")
                        else:
                            log("ℹ️ No entry plate to compare")
                    else:
                        log("⚠️ AI could not detect exit plate")
                        plate_number_exit = None
                        image_full_exit = None

                except Exception as e:
                    log(f"❌ AI scan failed at exit: {e}")
                    plate_number_exit = None
                    image_full_exit = None

                # Open gate
                client.publish("parking/gate/cmd", "OPEN_EXIT")
                log("🚪 Mở cổng ra")

                # Get slot info
                with db.cursor() as cur:
                    cur.execute("SELECT SlotID FROM parkingslot WHERE CurrentRFID=%s LIMIT 1", (rfid,))
                    slotRow = cur.fetchone()

                if slotRow:
                    slotIdExit = slotRow["SlotID"]

                    with db.cursor() as cur:
                        # Create EXIT record with full data
                        cur.execute("""
                            INSERT INTO parkinghistory
                            (RFID, SlotID, TimeIn, TimeOut, Duration, Fee, ImageFull, PlateNumber)
                            SELECT 
                                RFID,
                                SlotID,
                                TimeIn,
                                NOW() as TimeOut,
                                TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) as Duration,
                                TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) * 10 as Fee,
                                %s as ImageFull,
                                %s as PlateNumber
                            FROM parkinghistory
                            WHERE RFID=%s AND TimeOut IS NULL
                            ORDER BY HistoryID DESC LIMIT 1
                        """, (image_full_exit, plate_number_exit, rfid))

                        # Update the ENTRY record to mark as processed
                        cur.execute("""
                            UPDATE parkinghistory
                            SET TimeOut = NOW()
                            WHERE RFID=%s AND TimeOut IS NULL
                            ORDER BY HistoryID DESC LIMIT 1
                        """, (rfid,))

                        # Free the slot
                        cur.execute("UPDATE parkingslot SET Status=0, CurrentRFID=NULL WHERE SlotID=%s", (slotIdExit,))

                    log(f"✅ Lưu EXIT: RFID={rfid}, Plate={plate_number_exit}, Slot={slotIdExit} freed")

            return

        # ==========================================
        # 4. LOG SLOT CHANGE (for ENTRY)
        # ==========================================
        if topic == "parking/log":
            data = json.loads(payload)

            if data.get("event") == "slot_change" and "slot" in data and "status" in data:
                slotCode = data["slot"]
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