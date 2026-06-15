<?php
require_once("../session_start.php");
include("connectSQL.php");

if (!isset($_POST['Email']) || !isset($_POST['Password'])) {
    header("Location: ../login.php");
    exit();
}

$email = $_POST['Email'];
$password = $_POST['Password'];

$stmt = $conn->prepare("SELECT * FROM information WHERE Email = ? LIMIT 1");
$stmt->bind_param("s", $email);
$stmt->execute();

$result = $stmt->get_result();

if ($row = $result->fetch_assoc()) {

    if (password_verify($password, $row['Password'])) {

        $_SESSION['LoginInto'] = "TRUE";
        $_SESSION['Role'] = $row['Role'] ?? 'Admin';
        session_regenerate_id(true);

        header("Location: ../home.php");
        exit();
    }

    session_destroy();
    header("Location: ../login.php?error=wrong");
    exit();

} else {
    header("Location: ../login.php?error=notfound");
    exit();
}