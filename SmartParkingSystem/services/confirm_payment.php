<?php
include("../php/connectSQL.php");

error_reporting(E_ALL);
ini_set('display_errors', 1);

// ===== 1. CHECK INPUT =====
if (!isset($_POST['id'])) {
    echo json_encode(["status" => "error", "msg" => "missing_id"]);
    exit;
}

$id = intval($_POST['id']);

// ===== 2. CHECK PAYMENT =====
$res = mysqli_query($conn, "
    SELECT PaymentID, RFID, Status
    FROM payments
    WHERE PaymentID = $id
    LIMIT 1
");

if (!$res || mysqli_num_rows($res) == 0) {
    echo json_encode(["status" => "error", "msg" => "not_found"]);
    exit;
}

$row = mysqli_fetch_assoc($res);

// ===== 3. ALREADY PAID =====
if ($row['Status'] === 'paid') {
    echo json_encode([
        "status" => "ok",
        "msg" => "already_paid",
        "paymentId" => $id,
        "rfid" => $row['RFID']
    ]);
    exit;
}

// ===== 4. UPDATE PAYMENT =====
$update = mysqli_query($conn, "
    UPDATE payments
    SET Status = 'paid',
        Notified = 0
    WHERE PaymentID = $id
");

if (!$update) {
    echo json_encode(["status" => "error", "msg" => "db_error"]);
    exit;
}

// ===== 5. SUCCESS RESPONSE =====
echo json_encode([
    "status" => "success",
    "paymentId" => $id,
    "rfid" => $row['RFID']
]);

?>