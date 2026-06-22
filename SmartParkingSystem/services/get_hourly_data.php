<?php

require_once("../php/connectSQL.php");

if(!isset($_GET['date'])){
    echo json_encode([]);
    exit();
}

$date = mysqli_real_escape_string(
    $conn,
    $_GET['date']
);

$sql = "
SELECT
    HOUR(TimeIn) AS Hour,
    COUNT(*) AS VehicleCount
FROM parkinghistory
WHERE DATE(TimeIn) = '$date'
GROUP BY HOUR(TimeIn)
ORDER BY Hour
";

$result = mysqli_query($conn,$sql);

$data = [];

while($row=mysqli_fetch_assoc($result)){
    $data[] = $row;
}

header('Content-Type: application/json');
echo json_encode($data);