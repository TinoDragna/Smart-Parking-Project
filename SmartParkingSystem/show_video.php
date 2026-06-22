<?php
include('session_start.php');
// CHỈ cho phép Admin truy cập
if (isset($_SESSION['LoginInto']) && $_SESSION['LoginInto'] == "TRUE" && isset($_SESSION['Role']) && $_SESSION['Role'] == "Admin") {
    $current = 'video';
    require_once("includes/header.php");
} else {
    header('Location: /Smart-Parking-Project/SmartParkingSystem/login.php');
    exit;
}
?>

<div class="wrap" style="background: url(image/3.jpg); padding-bottom: 20px; min-height: 100vh;">
    <div class="row" style="margin: 0; padding-top: 15px;">
        <div class="col-12" style="text-align: center; margin-bottom: 10px;">
            <h2 class="Title" style="color: white">VEHICLE VERIFICATION DASHBOARD</h2>
        </div>
    </div>

    <div class="row" style="margin: 0;">

        <!-- ==================== COLUMN 1: LEFT (INCOMING) ==================== -->
        <div class="col-sm-3" style="padding: 10px;">
            <div
                style="background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); height: 100%;">
                <h3 style="color: #006289; text-align: center; border-bottom: 2px solid #ccc; padding-bottom: 10px;">
                    INCOMING VEHICLE</h3>

                <div style="margin-top: 20px; font-size: 16px;">
                    <p><strong>Assigned Slot:</strong> <span id="entry_slot"
                            style="color: #d9534f; font-weight: bold;">--</span></p>
                    <p><strong>Entry Time:</strong> <span id="entry_time">--</span></p>
                    <p><strong>License Plate:</strong> <span id="entry_plate"
                            style="color: #5cb85c; font-weight: bold; font-size: 18px;">--</span></p>
                    <p><strong>RFID Card:</strong> <span id="entry_rfid">--</span></p>
                    <div style="text-align: center; margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px;">
                        <h5 style="color: #006289;">Scan QR to take path guide</h5>
                        <img id="entry_qr_code" src="" alt="QR Code"
                            style="width: 150px; height: 150px; display: none; margin: 0 auto;">
                    </div>
                </div>

                <!-- Cropped Entry Verification Images -->
                <div style="margin-top: 15px;">
                    <h5 style="color: #555; text-align: center;">Entry Scanned Face</h5>
                    <div
                        style="height: 100px; border: 2px dashed #999; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ddd; border-radius: 5px;">
                        <img id="saved_entry_face_img" src="" alt="Face Image"
                            style="max-height: 100%; max-width: 100%; display: none;">
                        <span id="saved_entry_face_placeholder">No Image</span>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <h5 style="color: #555; text-align: center;">Entry Scanned Plate</h5>
                    <div
                        style="height: 100px; border: 2px dashed #999; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ddd; border-radius: 5px;">
                        <img id="saved_entry_plate_img" src="" alt="Plate Image"
                            style="max-height: 100%; max-width: 100%; display: none;">
                        <span id="saved_entry_plate_placeholder">No Image</span>
                    </div>
                </div>

            </div>
        </div>

        <!-- ==================== COLUMN 2: CENTER (CAMERA & CROPS) ==================== -->
        <div class="col-sm-6" style="padding: 10px;">
            <div
                style="background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <h3 style="color: #006289; text-align: center; border-bottom: 2px solid #ccc; padding-bottom: 10px;">
                    LIVE CAMERA & SCAN</h3>

                <!-- TOP: Camera Feed -->
                <div style="text-align: center; margin-top: 10px;">
                    <h5 style="color: #555;">Live Camera Feed</h5>
                    <div class="row" style="margin: 0; justify-content: center;">
                        <div class="col-sm-6" style="padding: 5px;">
                            <h6 style="color: #006289; font-weight: bold;">Entrance Gate</h6>
                            <div style="border: 2px solid #006289; border-radius: 5px; overflow: hidden; background-color: #000; display: flex; align-items: center; justify-content: center; height: 240px;">
                                <img id="live_video_entry" src="https://iot.eiu.com.vn/pi5/?action=stream"
                                    alt="Entrance Camera Offline"
                                    style="width: 100%; height: 100%; object-fit: cover;">
                            </div>
                        </div>
                        <div class="col-sm-6" style="padding: 5px;">
                            <h6 style="color: #006289; font-weight: bold;">Exit Gate</h6>
                            <div style="border: 2px solid #006289; border-radius: 5px; overflow: hidden; background-color: #000; display: flex; align-items: center; justify-content: center; height: 240px;">
                                <img id="live_video_exit" src="https://iot.eiu.com.vn/pi5Picam/stream.mjpg"
                                    alt="Exit Camera Offline"
                                    style="width: 100%; height: 100%; object-fit: cover;">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- BOTTOM: Terminal Logs -->
                <div style="margin-top: 15px;">
                    <h5 style="color: #555; text-align: left; padding-left: 5px; font-family: monospace;">System Terminal</h5>
                    <div id="terminal_logs"
                        style="height: 150px; border: 1px solid #333; overflow-y: auto; background: #1e1e1e; color: #00ff00; border-radius: 5px; padding: 10px; font-family: monospace; font-size: 13px; text-align: left; white-space: pre-wrap;">Connecting to terminal...</div>
                </div>

            </div>
        </div>

        <!-- ==================== COLUMN 3: RIGHT (OUTGOING) ==================== -->
        <div class="col-sm-3" style="padding: 10px;">
            <div
                style="background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); height: 100%;">
                <h3 style="color: #006289; text-align: center; border-bottom: 2px solid #ccc; padding-bottom: 10px;">
                    OUTGOING VEHICLE</h3>

                <div style="margin-top: 20px; font-size: 16px;">
                    <p><strong>License Plate:</strong> <span id="exit_plate_text"
                            style="color: #5cb85c; font-weight: bold; font-size: 18px;">--</span></p>
                    <p><strong>Exit Time:</strong> <span id="exit_time">--</span></p>
                    <p><strong>Total Duration:</strong> <span id="exit_duration">--</span> mins</p>
                    <p><strong>Parking Fee:</strong> <span id="exit_fee"
                            style="color: #d9534f; font-weight: bold; font-size: 18px;">--</span></p>
                    <p><strong>RFID Card:</strong> <span id="exit_rfid">--</span></p>
                </div>

                <!-- Cropped Exit Verification Images -->
                <div style="margin-top: 15px;">
                    <h5 style="color: #555; text-align: center;">Exit Verified Face</h5>
                    <div
                        style="height: 100px; border: 2px dashed #999; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ddd; border-radius: 5px;">
                        <img id="exit_face_img" src="" alt="Exit Face Image"
                            style="max-height: 100%; max-width: 100%; display: none;">
                        <span id="exit_face_placeholder">No Image</span>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <h5 style="color: #555; text-align: center;">Exit Verified Plate</h5>
                    <div
                        style="height: 100px; border: 2px dashed #999; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ddd; border-radius: 5px;">
                        <!-- Note: DB currently doesn't save cropped plate for exit, only full image of exit -->
                        <img id="exit_plate_img" src="" alt="Exit Plate Image"
                            style="max-height: 100%; max-width: 100%; display: none;">
                        <span id="exit_plate_placeholder">No Image</span>
                    </div>
                </div>

            </div>
        </div>

    </div>
</div>

<script type="text/javascript">
    function fixImagePath(dbPath) {
        if (!dbPath) return "";
        // Normalize backslashes (Windows) to forward slashes
        let fixedPath = dbPath.replace(/\\/g, "/");

        // Map "../" to the project root URL
        if (fixedPath.startsWith("../")) {
            fixedPath = "/Smart-Parking-Project/" + fixedPath.substring(3);
        }
        return fixedPath;
    }

    function updateImage(imgId, placeholderId, srcPath) {
        const imgEl = document.getElementById(imgId);
        const placeholderEl = document.getElementById(placeholderId);
        if (srcPath) {
            imgEl.src = srcPath;
            imgEl.style.display = "block";
            placeholderEl.style.display = "none";
        } else {
            imgEl.src = "";
            imgEl.style.display = "none";
            placeholderEl.style.display = "block";
        }
    }

    function fetchLatestData() {
        fetch('services/get_latest_parking_event.php')
            .then(response => response.json())
            .then(data => {
                const entry = data.entry;
                const exit = data.exit;

                // == 1. EXIT COLUMN (RIGHT) ALWAYS UPDATES WITH LATEST EXIT ==
                if (exit) {
                    document.getElementById('exit_time').textContent = exit.TimeOut || "--";
                    document.getElementById('exit_duration').textContent = exit.Duration !== null ? exit.Duration : "--";

                    const feeText = exit.Fee !== null ? parseInt(exit.Fee).toLocaleString() + " VND" : "--";
                    document.getElementById('exit_fee').textContent = feeText;
                    document.getElementById('exit_rfid').textContent = exit.RFID || "--";
                    document.getElementById('exit_plate_text').textContent = exit.PlateNumberExit || "--";

                    let exitFaceSrc = fixImagePath(exit.FaceImageExit);
                    updateImage('exit_face_img', 'exit_face_placeholder', exitFaceSrc);

                    let exitPlateSrc = fixImagePath(exit.MinCropExit || exit.ImageFullExit);
                    updateImage('exit_plate_img', 'exit_plate_placeholder', exitPlateSrc);
                }

                // == 2. MULTI-COLUMN SYNC (COLUMN 1 & 2) ==
                // We want Column 1 and 2 to show the ENTRY information of the currently relevant vehicle.
                // If the latest activity is an exit, we should show that vehicle's ENTRY info for comparison.

                let mainEntry = entry;
                if (exit && entry) {
                    const tIn = new Date(entry.TimeIn || entry.timein).getTime();
                    const tOut = new Date(exit.TimeOut || exit.timeout).getTime();
                    // If exit is newer than the latest entry, or if they are the same vehicle,
                    // prioritize the 'exit' object as it contains synchronized entry+exit info.
                    if (tOut > tIn || (entry.RFID === exit.RFID && entry.TimeIn === exit.TimeIn)) {
                        mainEntry = exit;
                    }
                } else if (!entry && exit) {
                    mainEntry = exit;
                }

                if (mainEntry) {
                    // Check both casing for robustness
                    const slotID = mainEntry.SlotID || mainEntry.slotid;
                    const timeIn = mainEntry.TimeIn || mainEntry.timein;
                    const plate = mainEntry.PlateNumberEntry || mainEntry.platenumberentry;
                    const rfid = mainEntry.RFID || mainEntry.rfid;

                    document.getElementById('entry_slot').textContent = slotID || "N/A";
                    document.getElementById('entry_time').textContent = timeIn || "--";
                    document.getElementById('entry_plate').textContent = plate || "--";
                    document.getElementById('entry_rfid').textContent = rfid || "--";

                    // Thay '172.16.10.157' bằng IP LAN thực tế của máy chủ web
                    const serverIP = "172.16.10.168";//localhost:8080
                    if (rfid && plate && rfid !== "--" && plate !== "--") {
                        const qrLink = `http://${serverIP}/Smart-Parking-Project/SmartParkingSystem/qr_login.php?rfid=${rfid}&plate=${plate}`;
                        // Dùng API miễn phí để tạo ảnh QR
                        document.getElementById('entry_qr_code').src = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(qrLink)}`;
                        document.getElementById('entry_qr_code').style.display = "block";
                    }

                    let facePath = mainEntry.FaceImageEntry || mainEntry.faceimageentry;
                    let platePath = mainEntry.MinCropEntry || mainEntry.mincropentry || mainEntry.ImageFullEntry || mainEntry.imagefullentry;

                    updateImage('saved_entry_face_img', 'saved_entry_face_placeholder', fixImagePath(facePath));
                    updateImage('saved_entry_plate_img', 'saved_entry_plate_placeholder', fixImagePath(platePath));
                }
            })
            .catch(err => console.error("Error fetching live data: ", err));
    }

    // Fetch immediately, then every 2 seconds
    fetchLatestData();
    setInterval(fetchLatestData, 2000);

    // Fetch terminal logs from python flask server
    function fetchTerminalLogs() {
        fetch('http://127.0.0.1:5001/logs')//('http://172.16.10.168:5001/logs')
            .then(response => response.json())
            .then(logs => {
                const terminal = document.getElementById('terminal_logs');
                // Only scroll to bottom if user is already near bottom, to prevent forcing scroll
                const isScrolledToBottom = terminal.scrollHeight - terminal.clientHeight <= terminal.scrollTop + 20;
                terminal.innerHTML = logs.join('<br>');
                if (isScrolledToBottom) {
                    terminal.scrollTop = terminal.scrollHeight;
                }
            })
            .catch(err => {
                const terminal = document.getElementById('terminal_logs');
                terminal.innerHTML = "<span style='color: red;'>Lost connection to Python server at 127.0.0.1:5001</span>";
            });
    }

    fetchTerminalLogs();
    setInterval(fetchTerminalLogs, 1000);

</script>

<?php require_once("includes/footer.php"); ?>