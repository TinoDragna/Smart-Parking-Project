<?php
include("../php/connectSQL.php");
$sql = "SELECT SlotID, Area, SlotCode, Status, CurrentRFID FROM parkingslot ORDER BY SlotID";
$res = mysqli_query($conn, $sql);
$data = [];
while ($row = mysqli_fetch_assoc($res)) {
    $row['Status'] = (int)$row['Status'];
    $data[] = $row;
}
header('Content-Type: application/json');
echo json_encode($data);
?>
