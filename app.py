from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# =====================
# DB CONNECTION FACTORY
# =====================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="smartparking",
        password="cyber@2025",
        database="smart_parking"
    )

# =====================
# PARKING HISTORY LIST
# =====================
@app.route("/api/parkinghistory")
def parking_history():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT
            HistoryID,
            RFID,
            SlotID,
            TimeIn,
            TimeOut,
            Duration,
            Fee,
            PlateNumberEntry
        FROM parkinghistory
        ORDER BY TimeIn DESC
    """)
    data = cur.fetchall()
    db.close()
    return jsonify(data)

# =====================
# PARKING HISTORY DETAIL
# =====================
@app.route("/api/parkinghistory/<int:history_id>")
def parking_history_detail(history_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT
            HistoryID,
            RFID,
            SlotID,
            TimeIn,
            TimeOut,
            Duration,
            Fee,
            ImageFullEntry,
            PlateNumberEntry,
            FaceImageEntry,
            ImageFullExit,
            PlateNumberExit,
            FaceImageExit
        FROM parkinghistory
        WHERE HistoryID = %s
    """, (history_id,))
    
    row = cur.fetchone()
    db.close()
    return jsonify(row)

# =====================
# PARKING SLOT
# =====================
@app.route("/api/parkingslot")
def parkingslot():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT SlotID, Area, SlotCode, Status, CurrentRFID
        FROM parkingslot
        ORDER BY SlotID
    """)
    data = cur.fetchall()
    db.close()
    return jsonify(data)

# =====================
# RFID CARD
# =====================
@app.route("/api/rfidcard")
def rfidcard():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT RFID, OwnerName, VehiclePlate, Type
        FROM rfidcard
        ORDER BY RFID
    """)
    data = cur.fetchall()
    db.close()
    return jsonify(data)

# =====================
if __name__ == "__main__":
    app.run(port=5000, debug=True)
