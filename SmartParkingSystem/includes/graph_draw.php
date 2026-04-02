<?php
?>

<!-- Parking History Table -->
<h3 style="color:white;">Parking History</h3>
<div class="table-responsive">
    <table class="table table-bordered table-striped table-dark">
        <thead>
            <tr>
                <th>Slot</th>
                <th>RFID</th>
                <th>Plate</th>
                <th>Time In</th>
                <th>Time Out</th>
                <th>Duration</th>
                <th>Fee</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody id="parkingHistoryBody">
            <!-- JS render here -->
        </tbody>
    </table>
    <div class="text-center">
        <button id="toggleHistoryBtn" class="btn btn-primary" style="display:none; margin-top: 10px; margin-bottom: 20px;">
            Show More
        </button>
    </div>
</div>

<!-- Parking Slots Table -->
<h3 style="color:white;">Parking Slots</h3>
<div class="table-responsive">
    <table class="table table-bordered table-striped table-dark" id="parkingSlotsTable">
        <thead>
            <tr>
                <th>Slot</th>
                <th>Area</th>
                <th>SlotCode</th>
                <th>Status</th>
                <th>Current RFID</th>
            </tr>
        </thead>
        <tbody id="slotBody">

        </tbody>
    </table>
    <div class="text-center">
        <button id="toggleSlotBtn" class="btn btn-primary" style="display:none; margin-top: 10px; margin-bottom: 20px;">
            Show More
        </button>
    </div>

    <style>
        .hidden-row {
            display: none;
        }
    </style>
</div>

<!-- RFID Cards Table -->
<h3 style="color:white;">RFID Cards</h3>
<div class="table-responsive">
    <table class="table table-bordered table-striped table-dark">
        <thead>
            <tr>
                <th>RFID</th>
                <th>Owner</th>
                <th>Vehicle Plate</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody id="rfidBody">

        </tbody>
    </table>
    <div class="text-center">
        <button id="toggleRfidBtn" class="btn btn-primary" style="display:none; margin-top: 10px; margin-bottom: 20px;">
            Show More
        </button>
    </div>
</div>

<h3 style="color:white;">Payment Verification</h3>
<div class="table-responsive">
    <table class="table table-bordered table-striped table-dark">
    <thead>
        <tr>
            <th>PaymentID</th>   
            <th>RFID</th>
            <th>Amount</th>
            <th>Status</th>
            <th>QR</th>
        </tr>
    </thead>
    <tbody id="paymentBody">

    </tbody>
    </table>
    <div class="text-center">
        <button id="togglePaymentBtn" class="btn btn-primary" style="display:none; margin-top: 10px; margin-bottom: 20px;">
            Show More
        </button>
    </div>
</div>
<div style="text-align:center; margin-top:20px">
    <img id="qr-image" width="250">
    <p id="qr-info" style="color:white"></p>
</div>

<script>
    let allHistory = [];
    let historyExpanded = false;
    const HISTORY_LIMIT = 5;

    async function loadParkingHistory() {
        const res = await fetch('services/get_parking_history.php');
        allHistory = await res.json();
        renderHistory();
    }

    function renderHistory() {
        let html = "";
        const items = historyExpanded ? allHistory : allHistory.slice(0, HISTORY_LIMIT);
        items.forEach(row => {
            html += `
            <tr onclick="openPayment(${row.HistoryID}, '${row.RFID}', ${row.Fee ?? 0})" style="cursor:pointer">
                <td>${row.SlotID}</td>
                <td>${row.RFID}</td>
                <td>${row.PlateNumberEntry ?? '-'}</td>
                <td>${row.TimeIn}</td>
                <td>${row.TimeOut ?? '-'}</td>
                <td>${row.Duration ?? '-'}</td>
                <td>${row.Fee ?? '0.00'}</td>
                <td>
                    <button class="btn btn-sm btn-info"
                            onclick="showDetail(${row.HistoryID}); event.stopPropagation();">
                        Detail
                    </button>
                </td>
            </tr>`;
        });
        document.getElementById("parkingHistoryBody").innerHTML = html;
        const btn = document.getElementById("toggleHistoryBtn");
        if(allHistory.length > HISTORY_LIMIT) {
            btn.style.display = "inline-block";
            btn.textContent = historyExpanded ? "Show Less" : "Show More";
        } else {
            btn.style.display = "none";
        }
    }

    document.getElementById("toggleHistoryBtn").addEventListener("click", () => {
        historyExpanded = !historyExpanded;
        renderHistory();
    });

    async function showDetail(historyID) {
        const res = await fetch(`services/get_parking_history_detail.php?id=${historyID}`);
        const d = await res.json();

        let html = `
        <h5>History ID: ${d.HistoryID}</h5>
        <p><b>Slot:</b> ${d.SlotID}</p>
        <p><b>RFID:</b> ${d.RFID}</p>
        <p><b>Time In:</b> ${d.TimeIn}</p>
        <p><b>Time Out:</b> ${d.TimeOut ?? '-'}</p>
        <p><b>Duration:</b> ${d.Duration ?? '-'} min</p>
        <p><b>Fee:</b> ${d.Fee ?? '0.00'}</p>
        <hr>
        <h6>ENTRY</h6>
        ${renderImage(d.ImageFullEntry)}
        <p>Plate: ${d.PlateNumberEntry ?? '-'}</p>
        ${renderImage(d.FaceImageEntry)}
        <hr>
        <h6>EXIT</h6>
        ${renderImage(d.ImageFullExit)}
        <p>Plate: ${d.PlateNumberExit ?? '-'}</p>
        ${renderImage(d.FaceImageExit)}
    `;

        document.getElementById("detail-body").innerHTML = html;
        $('#detailModal').modal('show');
    }

    function renderImage(src) {
        if (!src) return "<p>-</p>";
        return `<img src="${src}" class="img-fluid mb-2" style="max-width:100%">`;
    }

    document.addEventListener("DOMContentLoaded", loadParkingHistory);
</script>

<script>
    function openPayment(historyID, rfid, fee){

        if(!fee || fee==0){

            alert("Vehicle has not checked out yet.");

            return;
        }

        const bank="stb";
        const account="057419009999";
        const name="PHAM NGUYEN BAO TRANG";

        const qr=`https://img.vietqr.io/image/${bank}-${account}-compact.png?amount=${fee}&addInfo=PAY${historyID}&accountName=${name}`;

        document.getElementById("qr-image").src=qr;

        document.getElementById("qr-info").innerHTML =
            "RFID: "+rfid+" | Amount: "+fee+" VND";

        window.scrollTo({
            top:document.body.scrollHeight,
            behavior:"smooth"
        });
    }
</script>

<script>
    let allPayments = [];
    let paymentExpanded = false;
    const PAYMENT_LIMIT = 5;

    async function loadPayments(){
        const res = await fetch("/Smart-Parking-Project/SmartParkingSystem/services/get_payments.php");
        allPayments = await res.json();
        renderPayments();
    }
    
    function renderPayments() {
        const body = document.getElementById("paymentBody");
        let html = "";
        const items = paymentExpanded ? allPayments : allPayments.slice(0, PAYMENT_LIMIT);
        items.forEach(p=>{
            let btn="";
            if(p.Status=="pending"){
                btn=`<button onclick="showQR(${p.PaymentID},${p.Amount})" class="btn btn-info btn-sm">QR</button>`;
            }else{
                btn=`<span style="color:lightgreen">Paid</span>`;
            }
            html += `
            <tr>
                <td>${p.PaymentID}</td>
                <td>${p.RFID}</td>
                <td>${p.Amount}</td>
                <td>${p.Status}</td>
                <td>${btn}</td>
            </tr>
            `;
        });
        body.innerHTML = html;
        const btn = document.getElementById("togglePaymentBtn");
        if(allPayments.length > PAYMENT_LIMIT) {
            btn.style.display = "inline-block";
            btn.textContent = paymentExpanded ? "Show Less" : "Show More";
        } else {
            btn.style.display = "none";
        }
    }

    document.getElementById("togglePaymentBtn").addEventListener("click", () => {
        paymentExpanded = !paymentExpanded;
        renderPayments();
    });

    setInterval(loadPayments,3000);
    loadPayments();

    function showQR(id,amount){
        const bank="stb";
        const account="057419009999";
        const name="PHAM NGUYEN BAO TRANG";
        const qr=`https://img.vietqr.io/image/${bank}-${account}-compact.png?amount=${amount}&addInfo=PAY${id}&accountName=${name}`;

        document.getElementById("qr-image").src=qr;
        document.getElementById("qr-info").innerHTML =
        "Payment ID: "+id+" | Amount: "+amount+" VND";
    }

    async function autoShowQR(){
        const res=await fetch("services/get_latest_payment.php");
        const p=await res.json();
        if(!p) return;
        showQR(p.PaymentID,p.Amount);
        }
    setInterval(autoShowQR,3000);
</script>

<script>
    let allSlots = [];
    let expanded = false;
    const SHOW_LIMIT = 5;

    async function loadParkingSlots() {
        const res = await fetch("services/get_parkingslot.php");
        allSlots = await res.json();
        renderSlots();
    }

    function renderSlots() {
        const tbody = document.getElementById("slotBody");
        tbody.innerHTML = "";

        const slotsToShow = expanded
            ? allSlots
            : allSlots.slice(0, SHOW_LIMIT);

        slotsToShow.forEach(s => {
            tbody.innerHTML += `
        <tr>
            <td>${s.SlotID}</td>
            <td>${s.Area}</td>
            <td>${s.SlotCode}</td>
            <td>${s.Status ? 'Occupied' : 'Available'}</td>
            <td>${s.CurrentRFID ?? '-'}</td>
        </tr>`;
        });

        const btn = document.getElementById("toggleSlotBtn");
        if (allSlots.length > SHOW_LIMIT) {
            btn.style.display = "inline-block";
            btn.textContent = expanded ? "Show Less" : "Show More";
        }
    }

    document.getElementById("toggleSlotBtn").addEventListener("click", () => {
        expanded = !expanded;
        renderSlots();
    });

    document.addEventListener("DOMContentLoaded", loadParkingSlots);
</script>

<script>
    let allRfid = [];
    let rfidExpanded = false;
    const RFID_LIMIT = 5;

    function loadRfid() {
        fetch("services/get_rfidcard.php")
            .then(res => res.json())
            .then(data => {
                allRfid = data;
                renderRfid();
            });
    }

    function renderRfid() {
        let html = "";
        const items = rfidExpanded ? allRfid : allRfid.slice(0, RFID_LIMIT);
        items.forEach(c => {
            html += `
            <tr>
                <td>${c.RFID}</td>
                <td>${c.OwnerName}</td>
                <td>${c.VehiclePlate}</td>
                <td>${c.Type}</td>
            </tr>`;
        });
        document.getElementById("rfidBody").innerHTML = html;
        const btn = document.getElementById("toggleRfidBtn");
        if (allRfid.length > RFID_LIMIT) {
            btn.style.display = "inline-block";
            btn.textContent = rfidExpanded ? "Show Less" : "Show More";
        } else {
            btn.style.display = "none";
        }
    }

    document.getElementById("toggleRfidBtn").addEventListener("click", () => {
        rfidExpanded = !rfidExpanded;
        renderRfid();
    });

    document.addEventListener("DOMContentLoaded", loadRfid);
</script>

<div class="modal fade" id="detailModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content bg-dark text-white">
            <div class="modal-header">
                <h5 class="modal-title">Parking Detail</h5>
                <button type="button" class="close text-white" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body" id="detail-body"></div>
        </div>
    </div>
</div>

<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>