<?php
include("connectSQL.php");

if (!isset($_POST['RegisterInto'])) {
    exit("Invalid request");
}

$Email = $_POST["EmailRegister"] ?? '';
$Password = $_POST["PasswordRegister"] ?? '';
$Confirm = $_POST["PasswordRegisterConfirm"] ?? '';
$Name = $_POST["Name"] ?? '';
$DOB = $_POST["DateOfBirth"] ?? '';
$Address = $_POST["Address"] ?? '';

// VALIDATION
if (
    empty($Email) || empty($Password) || empty($Confirm) ||
    empty($Name) || empty($DOB) || empty($Address) ||
    $Password !== $Confirm ||
    strlen($Password) < 5 ||
    !filter_var($Email, FILTER_VALIDATE_EMAIL)
) {
    exit("Register failed");
}

// CHECK duplicate email (RẤT NÊN CÓ)
$check = $conn->prepare("SELECT ID FROM information WHERE Email = ?");
$check->bind_param("s", $Email);
$check->execute();
$result = $check->get_result();

if ($result->num_rows > 0) {
    exit("Email already exists");
}

// HASH PASSWORD
$hashedPassword = password_hash($Password, PASSWORD_BCRYPT);

// INSERT
$stmt = $conn->prepare("
    INSERT INTO information (Email, Password, Name, DateOfBirth, Address)
    VALUES (?, ?, ?, ?, ?)
");

$stmt->bind_param("sssss", $Email, $hashedPassword, $Name, $DOB, $Address);

if ($stmt->execute()) {
    header("Location: ../login.php");
    exit();
} else {
    echo "Register failed";
}

$conn->close();
?>