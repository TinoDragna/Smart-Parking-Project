<?php
include("../php/connectSQL.php");
$sql = "SELECT HistoryID, RFID, SlotID, TimeIn, TimeOut, Duration, Fee, PlateNumberEntry FROM parkinghistory ORDER BY TimeIn DESC";
$res = mysqli_query($conn, $sql);
$data = [];
while ($row = mysqli_fetch_assoc($res)) { $data[] = $row; }
header('Content-Type: application/json');
echo json_encode($data);
?>
