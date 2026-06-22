<?php
include('session_start.php');
require_once("db_connect.php");

if (isset($_SESSION['Role']) && $_SESSION['Role'] == 'User' && isset($_SESSION['HistoryID'])) {
    $hid = $_SESSION['HistoryID'];
    $stmt = $conn->prepare("SELECT TimeOut FROM parkinghistory WHERE HistoryID = ?");
    $stmt->bind_param("i", $hid);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        if ($row['TimeOut'] !== null) {
            // Xe đã ra -> Hủy session
            session_destroy();
            echo json_encode(['status' => 'logged_out']);
            exit;
        }
    }
}
echo json_encode(['status' => 'active']);
?>