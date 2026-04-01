<?php

if(isset($_POST['Login'])){

	include("connectSQL.php");

 	$Email = $_POST["Email"];
 	$Password = $_POST["Password"];

	$result = mysqli_query($conn,"SELECT * FROM  information where Email like '$Email' and Password like '$Password';");

	if (mysqli_num_rows($result)>0) {
		session_start();// Khởi tạo Session
		$_SESSION['LoginInto']="TRUE";
		$_SESSION['Role'] = "Admin";
		header('Location: /Smart-Parking-Project/SmartParkingSystem/index.php');

		$conn->close();
	}
	else
	{
		$conn->close();
		echo "login no success";
	}
}

if(isset($_POST['Register'])) {
	header('Location: /Smart-Parking-Project/SmartParkingSystem/register.php');
}


?>