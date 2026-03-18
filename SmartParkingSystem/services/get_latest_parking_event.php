<?php
header('Content-Type: application/json');
include("../php/connectSQL.php");

$response = [
    "entry" => null,
    "exit" => null
];

// Lấy thông tin xe vào mới nhất (chưa ra)
$sql_entry = "
    SELECT 
        ph.HistoryID, ph.RFID, ph.TimeIn, ph.PlateNumberEntry, ph.FaceImageEntry,
        ps.SlotName
    FROM parkinghistory ph
    LEFT JOIN parkingslot ps ON ph.SlotID = ps.SlotID
    WHERE ph.TimeOut IS NULL
    ORDER BY ph.TimeIn DESC 
    LIMIT 1
";
$result_entry = mysqli_query($conn, $sql_entry);
if ($result_entry && mysqli_num_rows($result_entry) > 0) {
    $row = mysqli_fetch_assoc($result_entry);
    
    // Derive cropped plate path
    $fullCropPath = $row["ImageFullEntry"];
    if ($fullCropPath && strpos($fullCropPath, "full_crop_LP") !== false) {
        $row["MinCropEntry"] = str_replace("full_crop_LP", "min_crop_LP", $fullCropPath);
    } else {
        $row["MinCropEntry"] = "";
    }

    $response["entry"] = $row;
}

// Lấy thông tin xe ra mới nhất (đã ra)
$sql_exit = "
    SELECT 
        ph.HistoryID, ph.RFID, ph.TimeOut, ph.Duration, ph.Fee, ph.PlateNumberExit, ph.FaceImageExit
    FROM parkinghistory ph
    WHERE ph.TimeOut IS NOT NULL
    ORDER BY ph.TimeOut DESC 
    LIMIT 1
";
$result_exit = mysqli_query($conn, $sql_exit);
if ($result_exit && mysqli_num_rows($result_exit) > 0) {
    $response["exit"] = mysqli_fetch_assoc($result_exit);
}

mysqli_close($conn);

echo json_encode($response);
?>
