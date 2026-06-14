from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
import datetime
import sys
import os

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
# FORCE CHECKOUT
# =====================
@app.route("/admin/force-checkout/<int:history_id>", methods=["POST"])
def admin_force_checkout(history_id):
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # Lấy thông tin lượt xe kẹt
        cur.execute("""
            SELECT RFID, SlotID, TimeIn 
            FROM parkinghistory 
            WHERE HistoryID = %s AND TimeOut IS NULL
        """, (history_id,))
        row = cur.fetchone()
        
        if not row:
            db.close()
            return jsonify({"success": False, "message": "Xe đã ra hoặc không tồn tại!"}), 400
            
        rfid = row["RFID"]
        slot_id = row["SlotID"]
        time_in = row["TimeIn"]
        
        # Tính phí theo giờ thực tế
        duration = int((datetime.datetime.now() - time_in).total_seconds() / 60)
        hours = max(1, (duration + 59) // 60)
        fee = hours * 30000
        
        # 1. Ép chốt đóng lịch sử bằng tay
        cur.execute("""
            UPDATE parkinghistory
            SET TimeOut = NOW(),
                Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()),
                Fee = %s,
                PlateNumberExit = 'ADMIN_MANUAL'
            WHERE HistoryID = %s
        """, (fee, history_id))
        
        # 2. Giải phóng chuồng (nếu trước đó xe đã kịp vào chuồng)
        if slot_id:
            cur.execute("""
                UPDATE parkingslot
                SET Status = 0, CurrentRFID = NULL
                WHERE SlotID = %s
            """, (slot_id,))
            
        # 3. Tạo hóa đơn đã thu tiền bởi Admin
        cur.execute("""
            INSERT INTO payments (RFID, HistoryID, Amount, Status, Notified)
            VALUES (%s, %s, %s, 'paid', 1)
        """, (rfid, history_id, fee))
        
        db.commit()
        db.close()
        
        # Gửi MQTT và cập nhật map nếu có thể
        try:
            import paho.mqtt.client as mqtt
            client = mqtt.Client()
            client.connect("172.16.2.4", 1883, 60)
            client.publish("parking/gate/cmd", "OPEN_EXIT")
            
            # Cập nhật đường đi map/path
            sys.path.append(os.path.join(os.path.dirname(__file__), "License-Plate-Recognition"))
            from path_finder import find_path_by_slot
            find_path_by_slot("")
        except Exception as mqtt_err:
            print(f"MQTT or path finder error: {mqtt_err}")
            
        return jsonify({"success": True, "message": "Đã giải phóng xe và làm sạch thẻ thành công!"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# =====================
if __name__ == "__main__":
    app.run(port=5001, debug=True)
