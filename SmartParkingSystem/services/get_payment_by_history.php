<?php

include("../php/connectSQL.php");

$historyId = intval($_GET['historyId']);

$sql = "
SELECT *
FROM payments
WHERE HistoryID=$historyId
LIMIT 1
";

$res = mysqli_query($conn,$sql);

$row = mysqli_fetch_assoc($res);

header("Content-Type: application/json");

echo json_encode($row);