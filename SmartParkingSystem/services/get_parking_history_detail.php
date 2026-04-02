<?php
include("../php/connectSQL.php");
$id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$sql = "SELECT HistoryID, RFID, SlotID, TimeIn, TimeOut, Duration, Fee, ImageFullEntry, PlateNumberEntry, FaceImageEntry, ImageFullExit, PlateNumberExit, FaceImageExit FROM parkinghistory WHERE HistoryID = $id";
$res = mysqli_query($conn, $sql);
$data = mysqli_fetch_assoc($res);
header('Content-Type: application/json');
echo json_encode($data);
?>
