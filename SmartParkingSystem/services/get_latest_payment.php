<?php
include("../php/connectSQL.php");

$res = mysqli_query($conn,"
SELECT PaymentID, RFID, Amount, Status
FROM payments
WHERE Status='pending' OR Status='waiting'
ORDER BY PaymentID DESC LIMIT 1
");

if(!$res || mysqli_num_rows($res)==0){
    echo json_encode(["status"=>"empty"]);
    exit;
}

$row = mysqli_fetch_assoc($res);

echo json_encode([
    "paymentId"=>$row["PaymentID"],
    "rfid"=>$row["RFID"],
    "amount"=>$row["Amount"],
    "status"=>$row["Status"]
]);