<?php
include('session_start.php');
// Khai báo file kết nối database của bạn (sửa lại đường dẫn nếu cần)
require_once("db_connect.php"); 

if (isset($_GET['rfid']) && isset($_GET['plate'])) {
    $rfid = $_GET['rfid'];
    $plate = $_GET['plate'];

    // Kiểm tra xe có đang đậu trong bãi hay không (TimeOut IS NULL)
    $stmt = $conn->prepare("SELECT HistoryID, TimeIn FROM parkinghistory WHERE RFID = ? AND PlateNumberEntry = ? AND TimeOut IS NULL ORDER BY HistoryID DESC LIMIT 1");
    $stmt->bind_param("ss", $rfid, $plate);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        
        // Tạo Session cho User
        $_SESSION['LoginInto'] = "TRUE";
        $_SESSION['Role'] = "User";
        $_SESSION['UserRFID'] = $rfid;
        $_SESSION['HistoryID'] = $row['HistoryID'];

        // Chuyển hướng thẳng vào trang chỉ đường
        header("Location: path.php");
        exit();
    } else {
        die("<h3>The QR code is invalid, or the vehicle has already left the parking lot!</h3>");
    }
} else {
    die("<h3>Missing QR code information!</h3>");
}
?>