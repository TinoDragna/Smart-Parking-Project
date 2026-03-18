<?php
session_start();
if ($_SESSION['LoginInto'] == "TRUE") {
    $current = 'video';
    require_once("includes/header.php");
} else {
    header('Location: /Smart-Parking-Project/SmartParkingSystem/login.php');
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
            <div style="background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); height: 100%;">
                <h3 style="color: #006289; text-align: center; border-bottom: 2px solid #ccc; padding-bottom: 10px;">INCOMING VEHICLE</h3>
                
                <div style="margin-top: 20px; font-size: 16px;">
                    <p><strong>Assigned Slot:</strong> <span id="entry_slot" style="color: #d9534f; font-weight: bold;">--</span></p>
                    <p><strong>Entry Time:</strong> <span id="entry_time">--</span></p>
                    <p><strong>License Plate:</strong> <span id="entry_plate" style="color: #5cb85c; font-weight: bold; font-size: 18px;">--</span></p>
                    <p><strong>RFID Card:</strong> <span id="entry_rfid">--</span></p>
                </div>
            </div>
        </div>

        <!-- ==================== COLUMN 2: CENTER (CAMERA & CROPS) ==================== -->
        <div class="col-sm-6" style="padding: 10px;">
            <div style="background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <h3 style="color: #006289; text-align: center; border-bottom: 2px solid #ccc; padding-bottom: 10px;">LIVE CAMERA & SCAN</h3>
                
                <!-- TOP: Camera Feed -->
                <div style="text-align: center; margin-top: 10px;">
                    <h5 style="color: #555;">Live Camera Feed</h5>
                    <!-- The camera feed URL needs to point to the actual stream, assuming same as entry gate in control.php -->
                    <iframe width="100%" height="320" style="border: 2px solid #006289; border-radius: 5px; overflow: hidden;" scrolling="no" src="https://iot.eiu.com.vn/picam/cam_pic_new.php?pDelay=40000"></iframe>
                </div>

                <!-- BOTTOM: Cropped Images -->
                <div class="row" style="margin-top: 15px;">
                    <div class="col-sm-6" style="text-align: center;">
                        <h5 style="color: #555;">Scanned Face</h5>
                        <div style="height: 150px; border: 2px dashed #999; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ddd; border-radius: 5px;">
                            <img id="entry_face_img" src="" alt="Face Image" style="max-height: 100%; max-width: 100%; display: none;">
                            <span id="entry_face_placeholder">No Image</span>
                        </div>
                    </div>
                    <div class="col-sm-6" style="text-align: center;">
                        <h5 style="color: #555;">Scanned Plate</h5>
                        <div style="height: 150px; border: 2px dashed #999; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ddd; border-radius: 5px;">
                            <!-- Full image or cropped plate from backend -->
                            <img id="entry_plate_img" src="" alt="Plate Image" style="max-height: 100%; max-width: 100%; display: none;">
                            <span id="entry_plate_placeholder">No Image</span>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <!-- ==================== COLUMN 3: RIGHT (OUTGOING) ==================== -->
        <div class="col-sm-3" style="padding: 10px;">
            <div style="background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); height: 100%;">
                <h3 style="color: #006289; text-align: center; border-bottom: 2px solid #ccc; padding-bottom: 10px;">OUTGOING VEHICLE</h3>
                
                <div style="margin-top: 20px; font-size: 16px;">
                    <p><strong>Exit Time:</strong> <span id="exit_time">--</span></p>
                    <p><strong>Total Duration:</strong> <span id="exit_duration">--</span> mins</p>
                    <p><strong>Parking Fee:</strong> <span id="exit_fee" style="color: #d9534f; font-weight: bold; font-size: 18px;">--</span></p>
                    <p><strong>RFID Card:</strong> <span id="exit_rfid">--</span></p>
                </div>

                <!-- Cropped Exit Verification Images -->
                <div style="margin-top: 15px;">
                    <h5 style="color: #555; text-align: center;">Exit Verified Face</h5>
                    <div style="height: 100px; border: 2px dashed #999; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ddd; border-radius: 5px;">
                        <img id="exit_face_img" src="" alt="Exit Face Image" style="max-height: 100%; max-width: 100%; display: none;">
                        <span id="exit_face_placeholder">No Image</span>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <h5 style="color: #555; text-align: center;">Exit Verified Plate</h5>
                    <div style="height: 100px; border: 2px dashed #999; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #ddd; border-radius: 5px;">
                        <!-- Note: DB currently doesn't save cropped plate for exit, only full image of exit -->
                        <img id="exit_plate_img" src="" alt="Exit Plate Image" style="max-height: 100%; max-width: 100%; display: none;">
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
    // dbPath is typically "../smart_parking_data/..."
    // We want to serve it locally if possible. In this web structure, 
    // maybe we need an image proxy or we assume smart_parking_data is accessible via URL like /smart_parking_data/
    // Since htdocs has Smart-Parking-Project, the root might be /Smart-Parking-Project/smart_parking_data/
    
    // For now, let's map "../" to "/Smart-Parking-Project/"
    let fixedPath = dbPath;
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
            // == ENTRY DATA ==
            const entry = data.entry;
            if (entry) {
                document.getElementById('entry_slot').textContent = entry.SlotName || "N/A";
                document.getElementById('entry_time').textContent = entry.TimeIn || "--";
                document.getElementById('entry_plate').textContent = entry.PlateNumberEntry || "--";
                document.getElementById('entry_rfid').textContent = entry.RFID || "--";
                
                let faceSrc = fixImagePath(entry.FaceImageEntry);
                updateImage('entry_face_img', 'entry_face_placeholder', faceSrc);
                
                let plateSrc = fixImagePath(entry.MinCropEntry || entry.ImageFullEntry);
                updateImage('entry_plate_img', 'entry_plate_placeholder', plateSrc);
            }

            // == EXIT DATA ==
            const exit = data.exit;
            if (exit) {
                document.getElementById('exit_time').textContent = exit.TimeOut || "--";
                document.getElementById('exit_duration').textContent = exit.Duration !== null ? exit.Duration : "--";
                
                const feeText = exit.Fee !== null ? parseInt(exit.Fee).toLocaleString() + " VND" : "--";
                document.getElementById('exit_fee').textContent = feeText;
                document.getElementById('exit_rfid').textContent = exit.RFID || "--";

                let exitFaceSrc = fixImagePath(exit.FaceImageExit);
                updateImage('exit_face_img', 'exit_face_placeholder', exitFaceSrc);
                
                // Exit Plate image
            }
        })
        .catch(err => console.error("Error fetching live data: ", err));
}

// Fetch immediately, then every 2 seconds
fetchLatestData();
setInterval(fetchLatestData, 2000);

</script>

<?php require_once("includes/footer.php"); ?>