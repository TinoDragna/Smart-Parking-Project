<?php
include("../php/connectSQL.php");

$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Select the slots with their grid coordinates
$sql = "
SELECT 
    CONCAT(Area, SlotCode) AS SlotName,
    GridCol,
    GridRow,
    Status,
    Direction
FROM parkingslot
ORDER BY Area, SlotCode
";

$result = $conn->query($sql);

$slots = [];
while ($row = $result->fetch_assoc()) {
    $slots[] = [
        "SlotName"    => $row["SlotName"],
        "coordinates" => [
            "col" => (int)$row["GridCol"],
            "row" => (int)$row["GridRow"]
        ],
        "Status"      => (int)$row["Status"],
        "Direction"  => $row["Direction"]
    ];
}

header('Content-Type: application/json');
echo json_encode($slots);

$conn->close();
?>