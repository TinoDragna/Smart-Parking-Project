import pymysql 
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plate_scanner import scan_plate

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# ================================
# DB CONNECTION
# ================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "smart_parking",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True
}

try:
    db = pymysql.connect(**DB_CONFIG)
    log("✅ DB connected")
except Exception as e:
    log(f"❌ DB connect failed with smartparking user: {e}")
    log("ℹ️  Trying root user...")
    try:
        DB_CONFIG["user"] = "root"
        DB_CONFIG["password"] = ""
        db = pymysql.connect(**DB_CONFIG)
        log("✅ DB connected with root user")
    except Exception as e2:
        log(f"❌ All DB connections failed: {e2}")
        exit(1)

print("\n" + "="*80)
print("🚗 MANUAL EXIT TEST - Simulating RFID Exit + AI Scan")
print("="*80)

# ================================
# TEST RFID
# ================================
TEST_RFID = "TESTRFID01"

print(f"\n1️⃣ Testing EXIT for RFID: {TEST_RFID}")
print("-"*80)

# Check if vehicle is inside
with db.cursor() as cur:
    cur.execute("""
        SELECT HistoryID, TimeIn, PlateNumber, ImageFull
        FROM parkinghistory 
        WHERE RFID=%s AND TimeOut IS NULL
        ORDER BY HistoryID DESC
        LIMIT 1
    """, (TEST_RFID,))
    entry_record = cur.fetchone()

if not entry_record:
    log(f"❌ RFID {TEST_RFID} has no active ENTRY (vehicle not inside)")
    log("ℹ️  Please run test_manual_entry.py first!")
    db.close()
    exit(1)

entry_history_id = entry_record['HistoryID']
entry_time = entry_record['TimeIn']
entry_plate = entry_record.get('PlateNumber')
entry_image = entry_record.get('ImageFull')

log(f"✅ Found active ENTRY record:")
log(f"   HistoryID: {entry_history_id}")
log(f"   TimeIn: {entry_time}")
log(f"   Entry Plate: {entry_plate}")
log(f"   Entry Image: {entry_image}")

# ================================
# SIMULATE EXIT WITH AI SCAN
# ================================
print(f"\n2️⃣ Simulating EXIT for RFID: {TEST_RFID}")
print("-"*80)

log("🤖 Starting AI license plate recognition for EXIT...")
log("ℹ️  Position a license plate in front of camera...")

try:
    image_full_exit, image_crop_exit, plate_number_exit = scan_plate()
    
    if plate_number_exit and plate_number_exit != "unknown":
        log(f"✅ AI detected exit plate: {plate_number_exit}")
        log(f"📁 Exit image: {image_full_exit}")

        # ===========================================
        # >>> ADDED: STRICT MATCH CHECK
        # ===========================================
        plate_match = False
        if entry_plate and plate_number_exit == entry_plate:
            log("✅ MATCH CONFIRMED: Entry plate == Exit plate")
            plate_match = True
        else:
            log(f"❌ PLATE MISMATCH: Entry={entry_plate} | Exit={plate_number_exit}")
            log("❌ NO GATE OPEN — EXIT BLOCKED")
            db.close()
            exit(0)     # STOP HERE. Do NOT save DB.

        # ===========================================
        # ONLY IF MATCH → NEW CODE BELOW RUNS
        # ===========================================

        # Calculate duration and fee
        with db.cursor() as cur:
            cur.execute("""
                SELECT 
                    TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) as duration,
                    TIMESTAMPDIFF(MINUTE, TimeIn, NOW()) * 10 as fee
                FROM parkinghistory
                WHERE HistoryID=%s
            """, (entry_history_id,))
            calc = cur.fetchone()
            
            duration = calc['duration'] if calc else 0
            fee = calc['fee'] if calc else 0
        
        log(f"💰 Calculated: Duration={duration} minutes, Fee={fee} VND")
        
        # Update the ENTRY record with exit info
        with db.cursor() as cur:
            cur.execute("""
                UPDATE parkinghistory
                SET 
                    TimeOut = NOW(),
                    Duration = %s,
                    Fee = %s,
                    ImageFull = CASE 
                        WHEN ImageFull IS NULL THEN %s
                        ELSE CONCAT(ImageFull, '|', %s)
                    END,
                    PlateNumber = CASE
                        WHEN PlateNumber IS NULL THEN %s
                        ELSE CONCAT(PlateNumber, '|', %s)
                    END
                WHERE HistoryID=%s
            """, (duration, fee, image_full_exit, image_full_exit, 
                  plate_number_exit, plate_number_exit, entry_history_id))
        
        # Free slot if exists
        with db.cursor() as cur:
            cur.execute("SELECT SlotID FROM parkingslot WHERE CurrentRFID=%s", (TEST_RFID,))
            slot_row = cur.fetchone()
            
            if slot_row:
                slot_id = slot_row['SlotID']
                cur.execute("UPDATE parkingslot SET Status=0, CurrentRFID=NULL WHERE SlotID=%s", (slot_id,))
                log(f"✅ Freed slot: {slot_id}")

        # ===========================================
        # >>> ADDED: PRINT GATE OPEN
        # ===========================================
        log("🔓🔓🔓 GATE OPEN — VEHICLE EXIT ALLOWED 🔓🔓🔓")

        log(f"✅ EXIT saved to database!")
        log(f"   Entry Plate: {entry_plate}")
        log(f"   Exit Plate: {plate_number_exit}")
        log(f"   Match: {plate_match}")
        log(f"   Duration: {duration} minutes")
        log(f"   Fee: {fee} VND")
        
        print("\n" + "="*80)
        print("✅ EXIT TEST SUCCESSFUL!")
        print("="*80)
        
        # Show the updated record
        with db.cursor() as cur:
            cur.execute("""
                SELECT HistoryID, RFID, SlotID, TimeIn, TimeOut, Duration, Fee, PlateNumber, ImageFull
                FROM parkinghistory 
                WHERE HistoryID=%s
            """, (entry_history_id,))
            record = cur.fetchone()
        
        print(f"\n📋 Updated Database Record:")
        for key, value in record.items():
            if key == 'ImageFull' and value and '|' in value:
                images = value.split('|')
                print(f"   {key}:")
                print(f"      Entry: {images[0]}")
                print(f"      Exit: {images[1]}")
            elif key == 'PlateNumber' and value and '|' in value:
                plates = value.split('|')
                print(f"   {key}:")
                print(f"      Entry: {plates[0]}")
                print(f"      Exit: {plates[1]}")
            else:
                print(f"   {key}: {value}")
        
    else:
        log("❌ No plate detected or scan cancelled")
        log("⚠️  EXIT NOT saved to database")
        
except Exception as e:
    log(f"❌ AI scan failed: {e}")
    import traceback
    traceback.print_exc()

db.close()
print("\n" + "="*80)
print("✅ Test complete!")
print("="*80)
