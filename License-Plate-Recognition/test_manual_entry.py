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
    "user": "root",  # Hoặc "smartparking"
    "password": "",  # Hoặc "cyber@2025"
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
print("🚗 MANUAL ENTRY TEST - Simulating RFID Entry + AI Scan")
print("="*80)

# ================================
# TEST RFID
# ================================
TEST_RFID = "TESTRFID01"

print(f"\n1️⃣ Testing RFID: {TEST_RFID}")
print("-"*80)

# Check if RFID exists in database
with db.cursor() as cur:
    cur.execute("SELECT RFID FROM rfidcard WHERE RFID=%s", (TEST_RFID,))
    exists = cur.fetchone()

if not exists:
    log(f"❌ RFID {TEST_RFID} not found in database!")
    log("ℹ️  Adding it now...")
    with db.cursor() as cur:
        cur.execute("INSERT INTO rfidcard (RFID) VALUES (%s)", (TEST_RFID,))
    log(f"✅ Added {TEST_RFID} to rfidcard table")
else:
    log(f"✅ RFID {TEST_RFID} exists in database")

# Check if vehicle is already inside
with db.cursor() as cur:
    cur.execute("SELECT HistoryID, TimeIn FROM parkinghistory WHERE RFID=%s AND TimeOut IS NULL", (TEST_RFID,))
    inside = cur.fetchone()

if inside:
    log(f"⚠️  Vehicle is already inside (HistoryID={inside['HistoryID']}, TimeIn={inside['TimeIn']})")
    user_input = input("   Do you want to EXIT this vehicle first? (y/n): ").strip().lower()
    
    if user_input == 'y':
        with db.cursor() as cur:
            cur.execute("""
                UPDATE parkinghistory 
                SET TimeOut=NOW(), Duration=TIMESTAMPDIFF(MINUTE, TimeIn, NOW()), Fee=TIMESTAMPDIFF(MINUTE, TimeIn, NOW())*10
                WHERE HistoryID=%s
            """, (inside['HistoryID'],))
            
            # Free slot if assigned
            cur.execute("UPDATE parkingslot SET Status=0, CurrentRFID=NULL WHERE CurrentRFID=%s", (TEST_RFID,))
        
        log("✅ Vehicle exited. Now you can test ENTRY again.")
    else:
        log("⏭️  Skipping ENTRY test since vehicle is already inside")
        db.close()
        exit(0)

# ================================
# SIMULATE ENTRY WITH AI SCAN
# ================================
print(f"\n2️⃣ Simulating ENTRY for RFID: {TEST_RFID}")
print("-"*80)

log("🤖 Starting AI license plate recognition...")
log("ℹ️  Position a license plate in front of camera...")

try:
    full_crop, min_crop, plate_number = scan_plate()
    
    if plate_number and plate_number != "unknown":
        log(f"✅ AI detected plate: {plate_number}")
        log(f"📁 Full image: {full_crop}")
        log(f"🔍 Crop image: {min_crop}")
        
        # Save to database
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO parkinghistory 
                (RFID, SlotID, TimeIn, ImageFull, PlateNumber)
                VALUES (%s, NULL, NOW(), %s, %s)
            """, (TEST_RFID, full_crop, plate_number))
            
            # Get the inserted ID
            history_id = cur.lastrowid
        
        log(f"✅ ENTRY saved to database!")
        log(f"   HistoryID: {history_id}")
        log(f"   RFID: {TEST_RFID}")
        log(f"   Plate: {plate_number}")
        log(f"   Image: {full_crop}")
        log(f"   TimeIn: NOW()")
        
        print("\n" + "="*80)
        print("✅ ENTRY TEST SUCCESSFUL!")
        print("="*80)
        
        # Show the record
        with db.cursor() as cur:
            cur.execute("""
                SELECT HistoryID, RFID, SlotID, TimeIn, TimeOut, PlateNumber, ImageFull
                FROM parkinghistory 
                WHERE HistoryID=%s
            """, (history_id,))
            record = cur.fetchone()
        
        print(f"\n📋 Database Record:")
        for key, value in record.items():
            print(f"   {key}: {value}")
        
    else:
        log("❌ No plate detected or scan cancelled")
        log("⚠️  Entry NOT saved to database")
        
except Exception as e:
    log(f"❌ AI scan failed: {e}")
    import traceback
    traceback.print_exc()

db.close()
print("\n" + "="*80)
print("✅ Test complete!")
print("="*80)