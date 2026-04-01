<?php
header('Content-Type: application/json');
include("../php/connectSQL.php");

$response = [
    "entry" => null,
    "exit" => null
];

// Lấy 1 dòng data mới nhất từ bảng history, không phân biệt xe đã ra hay chưa hay vẫn trong bãi
// Định nghĩa "mới nhất": Ưu tiên xe đang có tương tác tại cổng (ví dụ đang ở cổng ra chờ quét), sau đó xét theo thời gian TimeOut hoặc TimeIn mới nhất.
$sql = "
    SELECT 
        ph.HistoryID, ph.SlotID, ph.RFID, ph.TimeIn, ph.TimeOut, ph.Duration, ph.Fee, 
        ph.PlateNumberEntry, ph.FaceImageEntry, ph.ImageFullEntry,
        ph.PlateNumberExit, ph.FaceImageExit, ph.ImageFullExit,
        CONCAT(ps.Area, ps.SlotCode) AS SlotName
    FROM parkinghistory ph
    LEFT JOIN parkingslot ps ON ph.SlotID = ps.SlotID
    ORDER BY ph.HistoryID DESC 
    LIMIT 1
";

$result = mysqli_query($conn, $sql);
if ($result && mysqli_num_rows($result) > 0) {
    $row = mysqli_fetch_assoc($result);

    // Normalize paths Entry
    $row["ImageFullEntry"] = $row["ImageFullEntry"] ? str_replace("\\", "/", $row["ImageFullEntry"]) : "";
    $row["FaceImageEntry"] = $row["FaceImageEntry"] ? str_replace("\\", "/", $row["FaceImageEntry"]) : "";
    if ($row["ImageFullEntry"] && strpos($row["ImageFullEntry"], "full_crop_LP") !== false) {
        $row["MinCropEntry"] = str_replace("full_crop_LP", "min_crop_LP", $row["ImageFullEntry"]);
    } else {
        $row["MinCropEntry"] = "";
    }

    // Normalize paths Exit
    $row["ImageFullExit"] = $row["ImageFullExit"] ? str_replace("\\", "/", $row["ImageFullExit"]) : "";
    $row["FaceImageExit"] = $row["FaceImageExit"] ? str_replace("\\", "/", $row["FaceImageExit"]) : "";
    if ($row["ImageFullExit"] && strpos($row["ImageFullExit"], "full_crop_LP") !== false) {
        $row["MinCropExit"] = str_replace("full_crop_LP", "min_crop_LP", $row["ImageFullExit"]);
    } else {
        $row["MinCropExit"] = "";
    }

    $response["entry"] = $row;
    $response["exit"] = $row;
} else if (!$result) {
    $response["error"] = mysqli_error($conn);
}

mysqli_close($conn);

echo json_encode($response);
?>
