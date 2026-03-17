<?php
include("../php/connectSQL.php");

$id = intval($_POST['id']);

mysqli_query($conn,"
UPDATE payments
SET Status='waiting'
WHERE PaymentID=$id
");

echo "ok";