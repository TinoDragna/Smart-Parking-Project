<?php
require_once("session_start.php");
// Cho phép cả Admin và User truy cập
if (isset($_SESSION['LoginInto']) && $_SESSION['LoginInto'] == "TRUE") {
    $current = 'data'; // Hoặc 'data' bên file user_payment.php
    require_once("includes/header.php");
} else {
    header('Location: /Smart-Parking-Project/SmartParkingSystem/login.php');
    exit;
}
?>

<div class="wrap" style="background: url(image/3.jpg); min-height:100vh; padding:20px;">

    <div class="row">
        <div class="col-12" style="text-align:center;">
            <h2 class="Title" style="color:white;">QR PAYMENT</h2>
        </div>
    </div>

    <!-- KHU VỰC HIỂN THỊ -->
    <div id="payment-container" style="text-align:center; margin-top:40px;">
        <h4 style="color:white;">Waiting for vehicle...</h4>
    </div>

</div>

<script>

    let currentPaymentId = null;

    // ==============================
    // LOAD PAYMENT (KHÔNG RELOAD)
    // ==============================
    async function loadPayment() {

        try {
            const res = await fetch("services/get_latest_payment.php");
            const data = await res.json();

            const container = document.getElementById("payment-container");

            // ===== KHÔNG CÓ XE =====
            if (!data || data.status === "empty") {
                container.innerHTML = "<h4 style='color:white;'>Waiting for vehicle...</h4>";
                currentPaymentId = null;
                return;
            }

            // ===== TRÁNH RENDER LẠI LIÊN TỤC =====
            if (currentPaymentId === data.paymentId) {
                return;
            }

            currentPaymentId = data.paymentId;

            const bank = "vcb";
            const account = "123456789";
            const name = "SMART PARKING";

            const qr = `https://img.vietqr.io/image/${bank}-${account}-compact.png?amount=${data.amount}&addInfo=PAY${data.paymentId}&accountName=${name}`;

            let html = `
            <h4 style="color:white;">RFID: ${data.rfid}</h4>
            <h4 style="color:white;">Amount: ${data.amount} VND</h4>
            <img src="${qr}" style="width:250px; margin:20px;"><br>
        `;

            // ===== STATUS PENDING =====
            if (data.status === "pending") {
                html += `
                <button onclick="confirmPaid(${data.paymentId})"
                class="btn btn-success">
                I HAVE TRANSFERRED
                </button>
            `;
            }

            // ===== STATUS WAITING =====
            else if (data.status === "waiting") {
                html += `
                <h4 style="color:yellow;">
                    ⏳ Waiting for admin confirmation...
                </h4>
            `;
            }

            container.innerHTML = html;

        } catch (err) {
            console.error("Load payment error:", err);
        }
    }


    // ==============================
    // USER CLICK "I HAVE TRANSFERRED"
    // ==============================
    async function confirmPaid(id) {

        try {
            await fetch("services/confirm_user_payment.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: "id=" + id
            });

            // ===== RESET UI =====
            document.getElementById("payment-container").innerHTML =
                "<h4 style='color:white;'>⏳ Payment sent. Waiting for admin...</h4>";

            currentPaymentId = null;

        } catch (err) {
            console.error("Confirm error:", err);
        }
    }


    // ==============================
    // POLLING NHẸ (KHÔNG RELOAD)
    // ==============================
    setInterval(loadPayment, 2000);

    // load lần đầu
    loadPayment();

</script>

<script>
    setInterval(async function () {
        try {
            const res = await fetch("check_session_status.php");
            const data = await res.json();
            if (data.status === 'logged_out') {
                alert("Bạn đã rời bãi thành công. Tự động thoát tài khoản!");
                window.location.href = "login.php"; // Hoặc trang cảm ơn
            }
        } catch (err) { }
    }, 3000); // Kiểm tra 3s/lần
</script>

<?php require_once("includes/footer.php"); ?>