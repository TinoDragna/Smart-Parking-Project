<?php
// 🟢 Thêm ../ để đi ra thư mục cha bên ngoài lấy file session_start.php
include_once('../session_start.php'); 

if (isset($_POST['Login'])) {
    
    // 🟢 File connectSQL.php nếu cũng nằm trong folder php/ thì giữ nguyên, 
    // còn nếu nằm ở ngoài thì phải sửa thành "../connectSQL.php" 
    include("connectSQL.php"); 

    $Email = $_POST["Email"];
    $Password = $_POST["Password"];

    $result = mysqli_query($conn, "SELECT * FROM information where Email like '$Email' and Password like '$Password';");

    if (mysqli_num_rows($result) > 0) {
        
        session_regenerate_id(true);

        $_SESSION['LoginInto'] = "TRUE";
        $_SESSION['Role'] = "Admin";
        
        header('Location: /Smart-Parking-Project/SmartParkingSystem/index.php');
        $conn->close();
        exit;
    }
    else {
        $conn->close();
        echo "Login failed!";
    }
}

if (isset($_POST['Register'])) {
    header('Location: /Smart-Parking-Project/SmartParkingSystem/register.php');
    exit;
}
?>