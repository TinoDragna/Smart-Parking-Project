/* Wemos D1 R2 - Smart Parking (O/X, publish on change, block entry if full)
   - WiFi static kept as requested
   - MQTT broker: 172.16.2.4 (smartparking / cyber@2025)
   - Slots: A1=D0, B1=D4
   - Entry sensor: D3, Exit sensor: D5
   - Servos: entry D6, exit D7
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ===== WiFi (static) =====
const char* ssid = "CyberCenter";
const char* password = "";
IPAddress local_IP(172, 16, 10, 172);
IPAddress gateway(172, 16, 10, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress dns1(8,8,8,8);

// ===== MQTT =====
const char* mqtt_server = "172.16.2.4";
const uint16_t mqtt_port = 1883;
const char* mqtt_user = "smartparking";
const char* mqtt_pass = "cyber@2025";

WiFiClient netClient;
PubSubClient client(netClient);

// ===== LCD =====
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ===== Hardware pins =====
#define ENTRY_SENSOR_PIN D3
#define EXIT_SENSOR_PIN  D5
#define ENTRY_SERVO_PIN  D6
#define EXIT_SERVO_PIN   D7

#define OPEN_ANGLE  180
#define CLOSE_ANGLE 0
const unsigned long GATE_OPEN_MS = 3000UL; // auto-close ms

Servo entryGate, exitGate;

// ===== Slots =====
#define TOTAL_SLOTS 2
const int sensorPins[TOTAL_SLOTS] = { D0, D4 }; // A1, B1
const char* slotNames[TOTAL_SLOTS] = { "A1", "B1" };
bool slotOccupied[TOTAL_SLOTS] = { false, false };

// ===== RFID whitelist (offline) =====
String allowedUIDs[] = { "5E68200E", "90172383" };
const int whitelistSize = sizeof(allowedUIDs) / sizeof(allowedUIDs[0]);
bool rfidAuthorized = false;
String lastUID = "";
String rfidGate = ""; // ENTRY/EXIT

// ===== Gate states & timers =====
bool entryGateOpen = false;
bool exitGateOpen = false;
unsigned long entryOpenedAt = 0;
unsigned long exitOpenedAt = 0;

// ===== LCD cache to avoid flicker =====
String lastLCDLine1 = "";
String lastLCDLine2 = "";

//
bool lastEntryIR = HIGH;    // LOW = có xe, HIGH = không xe
bool lastExitIR  = HIGH;

// ===== prototypes =====
void connectWiFi();
void mqttReconnect();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void checkRFID();
void statusGateIR();
void handleSlots();
void updateLCD();
void publishSlotChange(int idx);
void publishSlotsCount();
int countFreeSlots();
void openEntryGate(const char* by);
void closeEntryGate();
void openExitGate(const char* by);
void closeExitGate();
void sendGateStatus(const char* status);
void sendLog(const char* gate, const char* action, const char* by);
String cleanUID(String raw);

void setup() {
  Serial.begin(9600); // UNO -> WEMOS TX/RX (ensure level-shifter!)
  delay(50);

  // LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Smart Parking");

  // servos
  entryGate.attach(ENTRY_SERVO_PIN);
  exitGate.attach(EXIT_SERVO_PIN);
  entryGate.write(CLOSE_ANGLE);
  exitGate.write(CLOSE_ANGLE);

  // sensors
  pinMode(ENTRY_SENSOR_PIN, INPUT); // assume LOW when detected per your original code
  pinMode(EXIT_SENSOR_PIN, INPUT);
  for (int i = 0; i < TOTAL_SLOTS; ++i) pinMode(sensorPins[i], INPUT);

  // WiFi + MQTT
  WiFi.mode(WIFI_STA);
  WiFi.config(local_IP, gateway, subnet, dns1);
  WiFi.begin(ssid, password);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(200);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("IP: "); Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi not connected");
  }

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);

  // initial publish of slots states
  handleSlots(); // detect current status & publish if needed
  updateLCD();
}

void loop() {
  if (!client.connected()) mqttReconnect();
  client.loop();

  statusGateIR();
  checkRFID();       // read UID from UNO
  handleSlots();     // read sensors & publish on change

  // If RFID authorized and entry sensor detects car -> open entry if freeSlots>0
  if (rfidAuthorized && rfidGate == "ENTRY" && digitalRead(ENTRY_SENSOR_PIN) == LOW) {
    int freeSlots = countFreeSlots();
    if (freeSlots > 0) {
      openEntryGate("RFID");
    } else {
      // deny: full
      sendLog("ENTRY", "DENIED_FULL", lastUID.c_str());
      // optionally notify mqtt topic
      client.publish("parking/gate/status", "ENTRY_DENIED_FULL");
    }
    // keep authorized until after gate action; we won't auto-reset here, gate auto-close handles it
    rfidAuthorized = false; // avoid re-triggering repeatedly
    lastUID = "";
  }

  if (rfidAuthorized && rfidGate == "EXIT" && digitalRead(EXIT_SENSOR_PIN) == LOW) {
    openExitGate("RFID");
    rfidAuthorized = false;
    lastUID = "";
  }

  // auto-close gates without blocking
  unsigned long now = millis();
  if (entryGateOpen && entryOpenedAt && now - entryOpenedAt >= GATE_OPEN_MS) {
    closeEntryGate();
    entryOpenedAt = 0;
  }
  if (exitGateOpen && exitOpenedAt && now - exitOpenedAt >= GATE_OPEN_MS) {
    closeExitGate();
    exitOpenedAt = 0;
  }

  // small yield
  delay(20);
}

// ===== WiFi/MQTT helpers =====
void connectWiFi() {
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("Static IP config failed");
  }
  WiFi.begin(ssid, password);
  unsigned long s = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - s < 15000) {
    delay(200);
  }
}

void mqttReconnect() {
  if (!WiFi.isConnected()) return;
  while (!client.connected()) {
    String cid = "WEMOS_SP_";
    cid += String(ESP.getChipId(), HEX);
    if (client.connect(cid.c_str(), mqtt_user, mqtt_pass)) {
      client.subscribe("parking/gate/cmd");
      // on reconnect we can publish current snapshot
      publishSlotsCount();
      for (int i = 0; i < TOTAL_SLOTS; ++i) publishSlotChange(i);
      client.publish("parking/system/status", "ONLINE");
    } else {
      delay(2000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; ++i) msg += (char)payload[i];
  msg.trim();
  String t(topic);

  if (t == "parking/gate/cmd") {
    if (msg == "OPEN_ENTRY") openEntryGate("MQTT");
    else if (msg == "CLOSE_ENTRY") closeEntryGate();
    else if (msg == "OPEN_EXIT") openExitGate("MQTT");
    else if (msg == "CLOSE_EXIT") closeExitGate();
  }

  if (t == "parking/rfid/auth") {
    if (msg == "OPEN_ENTRY") openEntryGate("MQTT");
    else if (msg == "CLOSE_ENTRY") closeEntryGate();
    else if (msg == "OPEN_EXIT") openExitGate("MQTT");
    else if (msg == "CLOSE_EXIT") closeExitGate();
  }
}

// ===== RFID reading (UNO sends lines like: "UID: 90 17 23 83") =====
String cleanUID(String raw) {
  raw.trim();
  if (raw.startsWith("UID:") || raw.startsWith("uid:")) raw = raw.substring(raw.indexOf(':') + 1);
  String out = "";
  for (unsigned int i = 0; i < raw.length(); ++i) {
    char c = raw.charAt(i);
    if (isxdigit(c)) out += (char)toupper(c);
  }
  return out;
}

void checkRFID() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    // Xác định loại cổng
    if (line.startsWith("ENTRY:")) {
      rfidGate = "ENTRY";
      lastUID = cleanUID(line.substring(6)); // lấy phần sau ENTRY:
    } else if (line.startsWith("EXIT:")) {
      rfidGate = "EXIT";
      lastUID = cleanUID(line.substring(5)); // lấy phần sau EXIT:
    } else {
      // Không đúng định dạng
      return;
    }

    if (lastUID.length() == 0) return;

    Serial.println("RFID " + rfidGate + " UID: " + lastUID);

    // Kiểm tra whitelist
    bool ok = false;
    for (int i = 0; i < whitelistSize; ++i) {
      if (lastUID.equalsIgnoreCase(allowedUIDs[i])) {
        ok = true;
        break;
      }
    }

    if (ok) {
      rfidAuthorized = true;
      client.publish("parking/rfid", (rfidGate + ":" + lastUID).c_str());
      sendLog(rfidGate.c_str(), "ACCEPT", lastUID.c_str());
    } else {
      rfidAuthorized = false;
      client.publish("parking/rfid", (rfidGate + ":" + lastUID).c_str());
      sendLog(rfidGate.c_str(), "REJECT", lastUID.c_str());
    }
  }
}

void statusGateIR() {
  int entryState = digitalRead(ENTRY_SENSOR_PIN);
  int exitState  = digitalRead(EXIT_SENSOR_PIN);

  if (entryState != lastEntryIR) {
    lastEntryIR = entryState;
    if (entryState == LOW) {
      client.publish("parking/gate/entry/ir", "O"); // có xe tại cổng vào Occupied
    } else {
      client.publish("parking/gate/entry/ir", "X"); // không có xe
    }
  }

  if (exitState != lastExitIR) {
    lastExitIR = exitState;
    if (exitState == LOW) {
      client.publish("parking/gate/exit/ir", "O"); // có xe tại cổng ra
    } else {
      client.publish("parking/gate/exit/ir", "X");
    }
  }
}


// ===== Slot handling =====
void handleSlots() {
  bool changed = false;
  for (int i = 0; i < TOTAL_SLOTS; ++i) {
    bool detected = (digitalRead(sensorPins[i]) == LOW); // LOW = occupied per your original wiring
    if (detected != slotOccupied[i]) {
      slotOccupied[i] = detected;
      publishSlotChange(i);
      changed = true;
    }
  }
  if (changed) {
    publishSlotsCount();
    updateLCD();
  }
}

void publishSlotChange(int idx) {
  String topic = String("parking/slot/") + slotNames[idx] + "/status";
  const char* payload = slotOccupied[idx] ? "O" : "X"; // O = Occupied, X = Empty
  client.publish(topic.c_str(), payload);
  // log event
  char buf[128];
  snprintf(buf, sizeof(buf), "{\"event\":\"slot_change\",\"slot\":\"%s\",\"status\":\"%s\",\"time\":\"%lu\"}",
           slotNames[idx], payload, millis());
  client.publish("parking/log", buf);
}

void publishSlotsCount() {
  int freeSlots = countFreeSlots();
  String s = String(freeSlots);
  client.publish("parking/slots", s.c_str());
  // publish count topic for convenience
  client.publish("parking/slots/count", s.c_str());
}

// ===== Utility =====
int countFreeSlots() {
  int c = 0;
  for (int i = 0; i < TOTAL_SLOTS; ++i) if (!slotOccupied[i]) ++c;
  return c;
}

// ===== Gate control =====
void openEntryGate(const char* by) {
  // double-check free slots before opening
  if (countFreeSlots() == 0) {
    sendLog("ENTRY", "DENIED_FULL", by);
    client.publish("parking/gate/status", "ENTRY_DENIED_FULL");
    return;
  }
  entryGate.write(OPEN_ANGLE);
  entryGateOpen = true;
  entryOpenedAt = millis();
  sendGateStatus("ENTRY_OPEN");
  sendLog("ENTRY", "OPEN", by);
  updateLCD();
}

void closeEntryGate() {
  entryGate.write(CLOSE_ANGLE);
  entryGateOpen = false;
  sendGateStatus("ENTRY_CLOSE");
  sendLog("ENTRY", "CLOSE", "SYSTEM");
  updateLCD();
}

void openExitGate(const char* by) {
  exitGate.write(OPEN_ANGLE);
  exitGateOpen = true;
  exitOpenedAt = millis();
  sendGateStatus("EXIT_OPEN");
  sendLog("EXIT", "OPEN", by);
  updateLCD();
}

void closeExitGate() {
  exitGate.write(CLOSE_ANGLE);
  exitGateOpen = false;
  sendGateStatus("EXIT_CLOSE");
  sendLog("EXIT", "CLOSE", "SYSTEM");
  updateLCD();
}

void sendGateStatus(const char* status) {
  client.publish("parking/gate/status", status);
}

void sendLog(const char* gate, const char* action, const char* by) {
  char logMsg[200];
  snprintf(logMsg, sizeof(logMsg), "{\"gate\":\"%s\",\"action\":\"%s\",\"by\":\"%s\",\"time\":\"%lu\"}",
           gate, action, by, millis());
  client.publish("parking/log", logMsg);
}

// ===== LCD update (O = occupied, X = empty) =====
void updateLCD() {
  String line1 = "";
  for (int i = 0; i < TOTAL_SLOTS; ++i) {
    line1 += slotNames[i];
    line1 += ":";
    line1 += (slotOccupied[i] ? "O" : "X");
    if (i < TOTAL_SLOTS - 1) line1 += " ";
  }
  String line2 = "Gate: ";
  if (entryGateOpen) line2 += "Entry O";
  else if (exitGateOpen) line2 += "Exit O";
  else line2 += "Closed";

  if (line1 != lastLCDLine1 || line2 != lastLCDLine2) {
    lcd.clear();
    lcd.setCursor(0,0); lcd.print(line1);
    lcd.setCursor(0,1); lcd.print(line2);
    lastLCDLine1 = line1;
    lastLCDLine2 = line2;
  }
}
