<?php
include("../php/connectSQL.php");

if(!isset($_POST['rfid'])){
    echo json_encode(["status"=>"error"]);
    exit;
}

$rfid = mysqli_real_escape_string($conn, $_POST['rfid']);

// lấy payment pending mới nhất
$res = mysqli_query($conn,"
SELECT PaymentID, RFID, Amount
FROM payments
WHERE RFID='$rfid' AND Status='pending'
ORDER BY PaymentID DESC LIMIT 1
");

if(!$res || mysqli_num_rows($res)==0){
    echo json_encode(["status"=>"no_payment"]);
    exit;
}

$row = mysqli_fetch_assoc($res);

// update sang waiting (user đang chuyển khoản)
mysqli_query($conn,"
UPDATE payments
SET Status='waiting'
WHERE PaymentID=".$row['PaymentID']."
");

echo json_encode([
    "status"=>"ok",
    "paymentId"=>$row['PaymentID'],
    "rfid"=>$row['RFID'],
    "amount"=>$row['Amount']
]);