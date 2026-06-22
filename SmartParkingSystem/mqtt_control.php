<?php
// 1. Khởi động session để đọc dữ liệu đăng nhập
if (session_status() === PHP_SESSION_NONE) {
    require_once("session_start.php");
}
session_write_close();

// Giữ Session mở tạm thời để bốc dữ liệu ra so khớp, sẽ đóng lại sau khi kiểm tra xong

// 2. CHỐT CHẶN BẢO MẬT: Kiểm tra quyền Admin + So khớp mã Anti-CSRF Token
if (
    isset($_SESSION['LoginInto']) && $_SESSION['LoginInto'] === "TRUE" && 
    isset($_SESSION['Role']) && $_SESSION['Role'] === "Admin" 
    && isset($_POST['csrf_token']) && $_POST['csrf_token'] === $_SESSION['csrf_token']
) {
    
    // 🟢 HỢP LỆ: Đã xác thực xong xuôi -> Đóng session ngay để tránh treo hệ thống bãi xe
    session_write_close();

    // Cho phép nạp thư viện và bắn MQTT
    require("phpMQTT.php"); 

    $server = "172.16.2.4"; 
    $port = 1883;
    $username = "";
    $password = "";
    $client_id = "php_control_" . uniqid();
    $topic = "parking/gate/cmd";

    if (isset($_POST['action'])) {
        $action = $_POST['action']; 

        $mqtt = new Bluerhinos\phpMQTT($server, $port, $client_id);
        if ($mqtt->connect(true, NULL, $username, $password)) {
            $mqtt->publish($topic, $action, 0);
            $mqtt->close();
            echo "OK - Command executed successfully by Admin with Valid Token";
        } else {
            echo "Failed to connect MQTT broker";
        }
    } else {
        echo "No action provided";
    }

} else {
    // 🔴 THẤT BẠI: Nếu là hacker (Không có Token hoặc sai mã bí mật) -> Giải phóng session và cấm cửa
    session_write_close();
    
    // Trả về mã lỗi 403 Forbidden (Bị từ chối truy cập) thay vì 401 để chuẩn chỉ về mặt kỹ thuật CSRF
    header("HTTP/1.1 403 Forbidden");
    echo "CSRF Attack Detected: Mã bảo mật Token không hợp lệ hoặc bị thiếu! Hệ thống phần cứng bãi xe đã chặn lệnh ngầm.";
    exit; 
}
?>
