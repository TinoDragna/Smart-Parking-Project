<?php

include("php/connectSQL.php");

$rfid = "TESTRFID03";

/* tìm xe đang trong bãi */

$sql = "
SELECT HistoryID, TimeIn
FROM parkinghistory
WHERE RFID='$rfid'
AND TimeOut IS NULL
ORDER BY HistoryID DESC
LIMIT 1
";

$res = mysqli_query($conn,$sql);

$row = mysqli_fetch_assoc($res);

if(!$row){

/* nếu chưa có thì tạo checkin */

mysqli_query($conn,"
INSERT INTO parkinghistory (RFID,TimeIn)
VALUES ('$rfid',NOW())
");

echo "Fake CHECKIN created";

exit;
}

$historyID = $row['HistoryID'];

/* fake checkout */

mysqli_query($conn,"
UPDATE parkinghistory
SET TimeOut = NOW()
WHERE HistoryID=$historyID
");

/* tính fee */

mysqli_query($conn,"
UPDATE parkinghistory
SET Duration = TIMESTAMPDIFF(MINUTE,TimeIn,TimeOut),
Fee = TIMESTAMPDIFF(MINUTE,TimeIn,TimeOut)*10
WHERE HistoryID=$historyID
");

/* lấy fee */

$res2 = mysqli_query($conn,"
SELECT Fee
FROM parkinghistory
WHERE HistoryID=$historyID
");

$d = mysqli_fetch_assoc($res2);

$fee = $d['Fee'];

/* tạo payment */

mysqli_query($conn,"
INSERT INTO payments (RFID,HistoryID,Amount,Status)
VALUES ('$rfid',$historyID,$fee,'pending')
");

echo "Fake checkout created<br>";
echo "Fee = $fee";

?>