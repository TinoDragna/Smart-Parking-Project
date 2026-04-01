<?php 
session_start();

if (isset($_SESSION['LoginInto']) && $_SESSION['LoginInto'] == "TRUE" && isset($_SESSION['Role']) && $_SESSION['Role'] == "Admin") {
    $current = 'data';
    require_once("includes/header.php");
} else {
    header('Location: /Smart-Parking-Project/SmartParkingSystem/login.php');
    exit;
}
?>

<div class="wrap" style="background: url(image/3.jpg); min-height:100vh; padding:20px;">
    
    <div class="row">
        <div class="col-12" style="text-align:center;">
            <h2 class="Title" style="color:white;">ADMIN PAYMENT MANAGEMENT</h2>
        </div>
    </div>

    <div class="row" style="margin-top:20px;">
        <div class="col-12">

            <table class="table table-bordered table-hover table-striped" 
                   style="background:white; border-radius:10px; overflow:hidden;">
                
                <thead class="thead-dark">
                    <tr>
                        <th>ID</th>
                        <th>RFID</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>

                <!-- 🔥 JS sẽ render vào đây -->
                <tbody id="paymentBody"></tbody>

            </table>

        </div>
    </div>
</div>

<script>

// ==============================
// LOAD PAYMENTS (REALTIME)
// ==============================
async function loadPayments(){

    try{
        const res = await fetch("services/get_payments.php?t=" + Date.now());
        const data = await res.json();

        const body = document.getElementById("paymentBody");

        let html = "";

        data.forEach(p=>{

            let status = "";
            let action = "";

            // ===== STATUS =====
            if(p.Status == "pending"){
                status = `<span class="badge badge-warning">Pending</span>`;
                action = `<span style="color:orange">Waiting User</span>`;
            }
            else if(p.Status == "waiting"){
                status = `<span class="badge badge-info">Waiting</span>`;
                action = `
                    <button onclick="confirmPayment(${p.PaymentID})"
                    class="btn btn-success btn-sm">
                        Confirm
                    </button>
                `;
            }
            else{
                status = `<span class="badge badge-success">Paid</span>`;
                action = `<span style="color:gray;">Done</span>`;
            }

            html += `
            <tr>
                <td>${p.PaymentID}</td>
                <td>${p.RFID}</td>
                <td>${p.Amount}</td>
                <td>${status}</td>
                <td style="text-align:center;">${action}</td>
            </tr>
            `;
        });

        body.innerHTML = html;

    }catch(err){
        console.error("Load payments error:", err);
    }
}


// ==============================
// ADMIN CONFIRM PAYMENT
// ==============================
function confirmPayment(id){

    fetch("services/confirm_payment.php",{
        method:"POST",
        headers:{
            "Content-Type":"application/x-www-form-urlencoded"
        },
        body:"id=" + id
    })
    .then(()=>{
        loadPayments(); // reload ngay
    });
}


// ==============================
// AUTO REFRESH
// ==============================
setInterval(loadPayments, 2000);

// load lần đầu
loadPayments();

</script>

<?php require_once("includes/footer.php"); ?>