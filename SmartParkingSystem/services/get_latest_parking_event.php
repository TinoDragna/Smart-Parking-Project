<?php
header('Content-Type: application/json');
include("../php/connectSQL.php");

$response = [
    "entry" => null,
    "exit" => null
];

// Lấy thông tin mới nhất từ bảng history (dù xe đã ra hay chưa)
$sql_entry = "
    SELECT 
        ph.SlotID, ph.RFID, ph.TimeIn, ph.PlateNumberEntry, ph.FaceImageEntry, ph.ImageFullEntry,
        ps.SlotName
    FROM parkinghistory ph
    LEFT JOIN parkingslot ps ON ph.SlotID = ps.SlotID
    ORDER BY ph.HistoryID DESC 
    LIMIT 1
";
$result_entry = mysqli_query($conn, $sql_entry);
if ($result_entry && mysqli_num_rows($result_entry) > 0) {
    $row = mysqli_fetch_assoc($result_entry);
    
    // Normalize and derive cropped plate path
    $fEntry = $row["ImageFullEntry"] ? str_replace("\\", "/", $row["ImageFullEntry"]) : "";
    $row["ImageFullEntry"] = $fEntry;
    $row["FaceImageEntry"] = $row["FaceImageEntry"] ? str_replace("\\", "/", $row["FaceImageEntry"]) : "";
    
    if ($fEntry && (strpos($fEntry, "full_crop_LP") !== false)) {
        $row["MinCropEntry"] = str_replace("full_crop_LP", "min_crop_LP", $fEntry);
    } else {
        $row["MinCropEntry"] = "";
    }

    $response["entry"] = $row;
}

// Lấy thông tin xe ra mới nhất (đã ra)
$sql_exit = "
    SELECT 
        ph.HistoryID,
        ph.SlotID,
        ph.RFID,
        ph.TimeIn,
        ph.TimeOut,
        ph.Duration,
        ph.Fee,
        ph.PlateNumberEntry,
        ph.PlateNumberExit,
        ph.FaceImageExit,
        ph.ImageFullExit,
        ph.FaceImageEntry,
        ph.ImageFullEntry
    FROM parkinghistory ph
    WHERE ph.TimeOut IS NOT NULL
    ORDER BY ph.TimeOut DESC 
    LIMIT 1
";
$result_exit = mysqli_query($conn, $sql_exit);
if ($result_exit && mysqli_num_rows($result_exit) > 0) {
    $row_exit = mysqli_fetch_assoc($result_exit);
    
    // Normalize and derive paths for exit
    $fExit = $row_exit["ImageFullExit"] ? str_replace("\\", "/", $row_exit["ImageFullExit"]) : "";
    $row_exit["ImageFullExit"] = $fExit;
    $row_exit["FaceImageExit"] = $row_exit["FaceImageExit"] ? str_replace("\\", "/", $row_exit["FaceImageExit"]) : "";
    
    if ($fExit && (strpos($fExit, "full_crop_LP") !== false)) {
        $row_exit["MinCropExit"] = str_replace("full_crop_LP", "min_crop_LP", $fExit);
    } else {
        $row_exit["MinCropExit"] = "";
    }
    
    // Normalize entry paths within exit object
    $fEntryEx = $row_exit["ImageFullEntry"] ? str_replace("\\", "/", $row_exit["ImageFullEntry"]) : "";
    $row_exit["ImageFullEntry"] = $fEntryEx;
    $row_exit["FaceImageEntry"] = $row_exit["FaceImageEntry"] ? str_replace("\\", "/", $row_exit["FaceImageEntry"]) : "";
    
    if ($fEntryEx && (strpos($fEntryEx, "full_crop_LP") !== false)) {
        $row_exit["MinCropEntry"] = str_replace("full_crop_LP", "min_crop_LP", $fEntryEx);
    } else {
        $row_exit["MinCropEntry"] = "";
    }
    
    $response["exit"] = $row_exit;
}

mysqli_close($conn);

echo json_encode($response);
?>
