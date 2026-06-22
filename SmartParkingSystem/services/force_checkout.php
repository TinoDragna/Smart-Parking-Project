<?php
header('Content-Type: application/json');

include('../session_start.php');
include('../php/connectSQL.php');

/* Kiểm tra quyền Admin */
if (
    !isset($_SESSION['LoginInto']) ||
    $_SESSION['LoginInto'] !== "TRUE" ||
    !isset($_SESSION['Role']) ||
    $_SESSION['Role'] !== "Admin"
) {
    echo json_encode([
        "success" => false,
        "message" => "Unauthorized access."
    ]);
    exit;
}

/* Kiểm tra dữ liệu gửi lên */
if (!isset($_POST['history_id'])) {
    echo json_encode([
        "success" => false,
        "message" => "Missing history_id."
    ]);
    exit;
}

$history_id = intval($_POST['history_id']);

try {

    /* Lấy lượt xe chưa checkout */
    $sql = "
        SELECT RFID, SlotID, TimeIn
        FROM parkinghistory
        WHERE HistoryID = ?
        AND TimeOut IS NULL
    ";

    $stmt = mysqli_prepare($conn, $sql);
    mysqli_stmt_bind_param($stmt, "i", $history_id);
    mysqli_stmt_execute($stmt);

    $result = mysqli_stmt_get_result($stmt);
    $row = mysqli_fetch_assoc($result);

    if (!$row) {
        echo json_encode([
            "success" => false,
            "message" => "Xe đã ra hoặc không tồn tại!"
        ]);
        exit;
    }

    $rfid = $row['RFID'];
    $slot_id = $row['SlotID'];
    $time_in = strtotime($row['TimeIn']);

    /* Tính thời gian gửi xe */
    $duration = floor((time() - $time_in) / 60);

    /* Làm tròn giờ */
    $hours = max(1, ceil($duration / 60));

    /* Tính phí */
    $fee = $hours * 30000;

    mysqli_begin_transaction($conn);

    /* 1. Đóng lịch sử gửi xe */
    $sql = "
        UPDATE parkinghistory
        SET
            TimeOut = NOW(),
            Duration = TIMESTAMPDIFF(MINUTE, TimeIn, NOW()),
            Fee = ?,
            PlateNumberExit = 'ADMIN_MANUAL'
        WHERE HistoryID = ?
    ";

    $stmt = mysqli_prepare($conn, $sql);
    mysqli_stmt_bind_param($stmt, "ii", $fee, $history_id);
    mysqli_stmt_execute($stmt);

    /* 2. Giải phóng slot */
    if (!empty($slot_id)) {

        $sql = "
            UPDATE parkingslot
            SET
                Status = 0,
                CurrentRFID = NULL
            WHERE SlotID = ?
        ";

        $stmt = mysqli_prepare($conn, $sql);
        mysqli_stmt_bind_param($stmt, "i", $slot_id);
        mysqli_stmt_execute($stmt);
    }

    /* 3. Tạo payment */
    $sql = "
        INSERT INTO payments
        (
            RFID,
            HistoryID,
            Amount,
            Status,
            Notified
        )
        VALUES
        (
            ?,
            ?,
            ?,
            'paid',
            1
        )
    ";

    $stmt = mysqli_prepare($conn, $sql);
    mysqli_stmt_bind_param(
        $stmt,
        "sii",
        $rfid,
        $history_id,
        $fee
    );

    mysqli_stmt_execute($stmt);

    mysqli_commit($conn);

    echo json_encode([
        "success" => true,
        "message" => "Đã giải phóng xe thành công!"
    ]);

} catch (Exception $e) {

    mysqli_rollback($conn);

    echo json_encode([
        "success" => false,
        "message" => $e->getMessage()
    ]);
}
?>