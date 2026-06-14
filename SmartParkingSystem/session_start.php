<?php
// Luôn cấu hình thông số Cookie an toàn TRƯỚC KHI chạy session
if (session_status() === PHP_SESSION_NONE) {
    session_set_cookie_params([
        'lifetime' => 0,              // Xóa cookie khi tắt trình duyệt
        'path' => '/',                // Có hiệu lực toàn bộ website
        'domain' => '',               // Để trống để tự động nhận diện localhost/IP
        'secure' => false,            // Đổi thành true nếu chạy HTTPS thực tế
        'httponly' => true,           // Chống JavaScript đọc trộm Session ID
        'samesite' => 'Strict'        // 🟢 Bật SameSite Strict để chống CSRF
    ]);
    session_start();
}
?>