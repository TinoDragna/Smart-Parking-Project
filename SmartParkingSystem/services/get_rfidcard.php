<?php
include("../php/connectSQL.php");
$sql = "SELECT RFID, OwnerName, VehiclePlate, Type FROM rfidcard ORDER BY RFID";
$res = mysqli_query($conn, $sql);
$data = [];
while ($row = mysqli_fetch_assoc($res)) { $data[] = $row; }
header('Content-Type: application/json');
echo json_encode($data);
?>
