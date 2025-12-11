import pymysql
from datetime import datetime
import sys
import os

# Add parent directory to path to import plate_scanner
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    log(f"❌ DB connect failed: {e}")
    log("ℹ️  Trying alternative config (root user, no password)...")
    try:
        DB_CONFIG["user"] = "root"
        DB_CONFIG["password"] = ""
        db = pymysql.connect(**DB_CONFIG)
        log("✅ DB connected with root user")
    except Exception as e2:
        log(f"❌ DB connect failed again: {e2}")
        exit(1)

print("\n" + "="*80)
print("📊 DATABASE INSPECTION")
print("="*80)

# ================================
# 1. Check RFID cards
# ================================
print("\n1️⃣ RFID Cards:")
print("-"*80)
try:
    with db.cursor() as cur:
        cur.execute("SELECT * FROM rfidcard LIMIT 10")
        cards = cur.fetchall()
    
    if cards:
        print(f"Found {len(cards)} RFID cards:")
        for card in cards:
            print(f"  - RFID: {card.get('RFID', 'N/A')}")
    else:
        print("  ❌ No RFID cards found")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ================================
# 2. Check specific RFID
# ================================
test_rfid = "90172383"
print(f"\n2️⃣ Checking RFID: {test_rfid}")
print("-"*80)
try:
    with db.cursor() as cur:
        cur.execute("SELECT * FROM rfidcard WHERE RFID=%s", (test_rfid,))
        card = cur.fetchone()
    
    if card:
        print(f"  ✅ RFID {test_rfid} exists in database")
        print(f"     Data: {card}")
    else:
        print(f"  ❌ RFID {test_rfid} NOT found in database")
        print(f"     Available RFIDs:")
        with db.cursor() as cur:
            cur.execute("SELECT RFID FROM rfidcard LIMIT 5")
            available = cur.fetchall()
        for a in available:
            print(f"       - {a['RFID']}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ================================
# 3. Check parking history
# ================================
print(f"\n3️⃣ Parking History for RFID: {test_rfid}")
print("-"*80)
try:
    with db.cursor() as cur:
        cur.execute("""
            SELECT HistoryID, RFID, SlotID, TimeIn, TimeOut, 
                   PlateNumber, ImageFull, Duration, Fee
            FROM parkinghistory 
            WHERE RFID=%s 
            ORDER BY HistoryID DESC 
            LIMIT 10
        """, (test_rfid,))
        records = cur.fetchall()
    
    if records:
        print(f"Found {len(records)} records:")
        print(f"\n{'ID':<5} | {'SlotID':<7} | {'TimeIn':<20} | {'TimeOut':<20} | {'Plate':<12} | {'Dur':<5} | {'Fee':<6}")
        print("-"*120)
        
        for r in records:
            history_id = r['HistoryID']
            slot_id = str(r['SlotID']) if r['SlotID'] is not None else 'NULL'
            time_in = str(r['TimeIn']) if r['TimeIn'] else 'NULL'
            time_out = str(r['TimeOut']) if r['TimeOut'] else 'NULL'
            plate = r['PlateNumber'] if r['PlateNumber'] else 'NULL'
            duration = str(r['Duration']) if r['Duration'] is not None else 'NULL'
            fee = str(r['Fee']) if r['Fee'] is not None else 'NULL'
            
            print(f"{history_id:<5} | {slot_id:<7} | {time_in:<20} | {time_out:<20} | {plate:<12} | {duration:<5} | {fee:<6}")
            
            if r['ImageFull']:
                print(f"       Image: {r['ImageFull']}")
    else:
        print(f"  ❌ No history records for RFID {test_rfid}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ================================
# 4. Check table structure
# ================================
print(f"\n4️⃣ Table Structure: parkinghistory")
print("-"*80)
try:
    with db.cursor() as cur:
        cur.execute("DESCRIBE parkinghistory")
        columns = cur.fetchall()
    
    print(f"{'Field':<20} | {'Type':<20} | {'Null':<5} | {'Key':<5}")
    print("-"*80)
    for col in columns:
        field = col['Field']
        col_type = col['Type']
        null = col['Null']
        key = col['Key']
        print(f"{field:<20} | {col_type:<20} | {null:<5} | {key:<5}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ================================
# 5. Check if columns exist
# ================================
print(f"\n5️⃣ Checking AI columns:")
print("-"*80)
try:
    with db.cursor() as cur:
        cur.execute("SHOW COLUMNS FROM parkinghistory LIKE 'PlateNumber'")
        plate_col = cur.fetchone()
        
        cur.execute("SHOW COLUMNS FROM parkinghistory LIKE 'ImageFull'")
        image_col = cur.fetchone()
    
    if plate_col:
        print("  ✅ Column 'PlateNumber' exists")
    else:
        print("  ❌ Column 'PlateNumber' MISSING - Run ALTER TABLE!")
        print("     ALTER TABLE parkinghistory ADD COLUMN PlateNumber VARCHAR(20);")
    
    if image_col:
        print("  ✅ Column 'ImageFull' exists")
    else:
        print("  ❌ Column 'ImageFull' MISSING - Run ALTER TABLE!")
        print("     ALTER TABLE parkinghistory ADD COLUMN ImageFull VARCHAR(255);")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# ================================
# 6. Active parking sessions
# ================================
print(f"\n6️⃣ Active Parking Sessions (TimeOut IS NULL):")
print("-"*80)
try:
    with db.cursor() as cur:
        cur.execute("""
            SELECT HistoryID, RFID, SlotID, TimeIn, PlateNumber
            FROM parkinghistory 
            WHERE TimeOut IS NULL
            ORDER BY TimeIn DESC
            LIMIT 10
        """)
        active = cur.fetchall()
    
    if active:
        print(f"Found {len(active)} active sessions:")
        for a in active:
            print(f"  - ID: {a['HistoryID']}, RFID: {a['RFID']}, Slot: {a['SlotID']}, "
                  f"TimeIn: {a['TimeIn']}, Plate: {a.get('PlateNumber', 'NULL')}")
    else:
        print("  ✅ No active sessions (all vehicles have exited)")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ================================
# 7. TEST AI LICENSE PLATE SCANNER
# ================================
print(f"\n7️⃣ Testing AI License Plate Scanner:")
print("-"*80)
print("ℹ️  This will open your webcam and scan for license plates")
print("ℹ️  Press 'q' to quit or wait for automatic detection")
print("⚠️  Make sure your webcam is connected!")

try:
    # Import the scan_plate function
    from plate_scanner import scan_plate
    
    user_input = input("\n🎥 Start camera test? (y/n): ").strip().lower()
    
    if user_input == 'y':
        log("🤖 Starting AI license plate recognition...")
        full_crop, min_crop, plate_number = scan_plate()
        
        if plate_number and plate_number != "unknown":
            print(f"\n✅ SUCCESS!")
            print(f"   📸 Full image: {full_crop}")
            print(f"   🔍 Plate crop: {min_crop}")
            print(f"   🚗 Plate number: {plate_number}")
        else:
            print(f"\n⚠️  No plate detected or scan cancelled")
    else:
        print("⏭️  Skipped camera test")
        
except ImportError:
    print("  ❌ Cannot import plate_scanner module")
    print("     Make sure plate_scanner.py is in the same directory")
except Exception as e:
    print(f"  ❌ Camera test error: {e}")

# ================================
# Close
# ================================
db.close()
print("\n" + "="*80)
print("✅ Database inspection complete!")
print("="*80)