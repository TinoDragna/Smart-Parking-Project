<?php

include("../php/connectSQL.php");

// ==============================
// CHỐNG CACHE (RẤT QUAN TRỌNG)
// ==============================
header("Cache-Control: no-cache, no-store, must-revalidate");
header("Pragma: no-cache");
header("Expires: 0");

// ==============================
// JSON HEADER
// ==============================
header("Content-Type: application/json; charset=UTF-8");

// ==============================
// QUERY
// ==============================
$sql = "
SELECT 
    p.PaymentID,
    p.RFID,
    p.Amount,
    p.Status,
    p.CreatedAt,

    ph.HistoryID,
    ph.TimeIn,
    ph.Duration,
    ph.Fee,
    ph.SlotID

FROM payments p

LEFT JOIN parkinghistory ph 
    ON p.HistoryID = ph.HistoryID

ORDER BY p.PaymentID DESC
";

// ==============================
// EXECUTE
// ==============================
$res = mysqli_query($conn, $sql);

$data = [];

if($res){
    while($row = mysqli_fetch_assoc($res)){

        // đảm bảo không null
        $data[] = [
            "PaymentID" => $row["PaymentID"],
            "RFID" => $row["RFID"],
            "Amount" => $row["Amount"],
            "Status" => $row["Status"],
            "CreatedAt" => $row["CreatedAt"],

            "HistoryID" => $row["HistoryID"] ?? null,
            "TimeIn" => $row["TimeIn"] ?? null,
            "Duration" => $row["Duration"] ?? null,
            "Fee" => $row["Fee"] ?? null,
            "SlotID" => $row["SlotID"] ?? null
        ];
    }
}

// ==============================
// OUTPUT
// ==============================
echo json_encode($data, JSON_UNESCAPED_UNICODE);

// ==============================
// CLOSE
// ==============================
mysqli_close($conn);