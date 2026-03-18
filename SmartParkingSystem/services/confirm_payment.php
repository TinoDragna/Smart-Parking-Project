<?php

include("../php/connectSQL.php");

$id=intval($_POST['id']);

mysqli_query($conn,"UPDATE payments SET Status='paid' WHERE PaymentID=$id");

require("../phpMQTT.php");

$mqtt=new Bluerhinos\phpMQTT("172.16.2.4",1883,"web_confirm");

if($mqtt->connect()){

$mqtt->publish("parking/gate/cmd","OPEN_EXIT",0);

$mqtt->close();

}

echo "ok";