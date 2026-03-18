<?php

include("../php/connectSQL.php");

$res=mysqli_query($conn,"SELECT * FROM payments ORDER BY PaymentID DESC");

$data=[];

while($row=mysqli_fetch_assoc($res)){
$data[]=$row;
}

echo json_encode($data);