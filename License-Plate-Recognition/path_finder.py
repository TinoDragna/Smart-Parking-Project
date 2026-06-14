from collections import deque

STEP = 0.5
MAX_COL = 5
MAX_ROW = 5
EXIT_KEY = "5.0,5.0"

import pymysql

def is_goal(current, slots, mode):
    k = key(current)
    slot = slots.get(k)

    if mode == "entry":
        return slot and slot["status"] == 0

    elif mode == "exit":
        return k == EXIT_KEY

    return False

def get_slots():
    conn = pymysql.connect(
        host="localhost",
        user="smartparking",
        password="cyber@2025",
        database="smart_parking",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

    slots = {}
    slot_lookup = {}  # 🔥 NEW

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT Area, SlotCode, GridCol, GridRow, Status FROM parkingslot")
            rows = cursor.fetchall()

            for r in rows:
                col = round(float(r["GridCol"]), 2)
                row = round(float(r["GridRow"]), 2)

                slot_name = f"{r['Area']}{r['SlotCode']}"

                slots[f"{col},{row}"] = {
                    "status": r["Status"],
                    "slot_name": slot_name
                }

                # 🔥 reverse mapping
                slot_lookup[slot_name] = {
                    "col": col,
                    "row": row
                }
    finally:
        conn.close()

    return slots, slot_lookup

from collections import deque

STEP = 0.5
MAX_COL = 5
MAX_ROW = 5

def key(node):
    return f"{round(node['col'],2)},{round(node['row'],2)}"

def is_valid(node):
    return 0 <= node["col"] <= MAX_COL and -0.5 <= node["row"] <= MAX_ROW

def get_neighbors(node, mode):
    col, row = node["col"], node["row"]

    # 🔥 stop if already at exit
    if mode == "exit" and key(node) == EXIT_KEY:
        return []

    # ENTRY special
    if col == 0 and row == 5:
        return [{"col": 0.0, "row": 4.5}]
    if col == 0 and row == 4.5:
        return [{"col": 0.5, "row": 4.5}]
    if col == 4.5 and row == 5:
        return [{"col": 5.0, "row": 5.0}]

    # ENTRY logic
    if mode == "entry":
        if col >= MAX_COL:
            return [{"col": col, "row": row + STEP}]
        if abs(row - round(row, 0) != 0):
            return [
                {"col": col, "row": row - STEP},    # then UP
                {"col": col + STEP, "row": row},   # 🔥 RIGHT first
            ]
        else:
            return [
                {"col": col + STEP, "row": row},   # 🔥 RIGHT first
                {"col": col, "row": row - STEP},    # then UP
            ]
    # EXIT logic
    if mode == "exit":

        is_slot = (abs(col - round(col)) < 1e-6) and (abs(row - round(row)) < 1e-6)

        # Phase 1: leave slot
        if is_slot:
            return [{"col": col + STEP, "row": row}]

        # Shortcut near exit
        if col >= 4.5 and row < MAX_ROW:
            return [{"col": col, "row": row + STEP}]

        # Phase 2: go UP
        if row > -0.5:
            return [{"col": col, "row": row - STEP}]

        # Phase 3: go RIGHT
        if abs(row - (-0.5)) < 1e-6 and col < MAX_COL:
            return [{"col": col + STEP, "row": row}]

        # Phase 4: go DOWN
        if col >= MAX_COL and row < MAX_ROW:
            return [{"col": col, "row": row + STEP}]
        
def reconstruct_path(parent, end_node):
    path = []
    current = end_node

    while current:
        path.append({
            "col": round(current["col"], 2),
            "row": round(current["row"], 2)
        })
        current = parent.get(key(current))

    path.reverse()

    return {
        "pathNodes": path,
        "type": "entry"
    }

def find_path(start, slots):
    mode = "entry" if start == {"col": 0, "row": 5} else "exit"

    queue = deque([start])
    visited = set()
    parent = {}

    visited.add(key(start))

    while queue:
        current = queue.popleft()

        # print(f"Visiting: {current['col']},{current['row']}")

        if is_goal(current, slots, mode):
            path = reconstruct_path(parent, current)

            if mode == "entry":
                slot = slots.get(key(current))
                print("✅ Found slot:", slot["slot_name"])
            else:
                print("✅ Reached EXIT")

            # print("Path:", path["pathNodes"])

            data = {
                "pathNodes": path["pathNodes"],
                "type": mode,
            }

            publish_path(data)
        
            return slot["slot_name"] if mode == "entry" else "EXIT"

        for neighbor in get_neighbors(current, mode):
            k = key(neighbor)

            if not is_valid(neighbor):
                continue

            if k in visited:
                continue

            # 🚫 block slot nodes unless they are the goal
            if mode == "entry":
                slot = slots.get(k)
                if slot and slot["status"] != 0:
                    continue
            elif mode == "exit":
                if k in slots and k != EXIT_KEY:
                    continue

            visited.add(k)
            parent[k] = current
            queue.append(neighbor)

    return None

def find_path_by_slot(slot_name):
    if slot_name == "":
        publish_path({})
        return
    slots, slot_lookup = get_slots()

    if slot_name not in slot_lookup:
        print("❌ Slot not found:", slot_name)
        return None

    start = slot_lookup[slot_name]

    return find_path(start, slots)

def is_slot_node(node, slots):
    return key(node) in slots

import json
import paho.mqtt.client as mqtt

def publish_path(data):
    client = mqtt.Client(transport="websockets")

    # connect to your broker
    client.connect("172.16.2.4", 9001, 60)

    payload = json.dumps(data)

    # print("📤 Publishing to map/path:", payload)

    client.loop_start()
    client.publish("map/path", payload)
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    print(find_path_by_slot("Entry"))