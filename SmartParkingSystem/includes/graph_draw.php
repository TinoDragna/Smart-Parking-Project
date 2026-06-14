<?php
?>
<!-- Parking History Table -->
<h3 style="color:white;">Parking History</h3>

<!-- Parking History Filters -->
<div class="col-12">
    <div class="filter-wrapper">
        <div class="mb-3">
            <form id="historyFilterForm" class="form-row">
                <div class="col-sm-2">
                    <input type="text" id="filterHistorySlot" class="form-control"
                        placeholder="Filter Slot">
                </div>
                <div class="col-sm-3">
                    <input type="text" id="filterHistoryRFID" class="form-control"
                        placeholder="Filter RFID">
                </div>
                <div class="col-sm-3">
                    <input type="text" id="filterHistoryPlate" class="form-control"
                        placeholder="Filter Plate">
                </div>
                <div class="col-sm-2">
                    <select id="filterHistoryStatus" class="form-control">
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="completed">Checked Out</option>
                    </select>
                </div>
                <div class="col-sm-2">
                    <button type="button" id="clearHistoryFilter"
                        class="btn btn-secondary btn-block">Clear</button>
                </div>
            </form>
        </div>
    </div>
</div>

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
        <button id="toggleHistoryBtn" class="btn btn-primary"
            style="display:none; margin-top: 10px; margin-bottom: 20px;">
            Show More
        </button>
    </div>
</div>

<!-- Parking Slots Table -->
<h3 style="color:white;">Parking Slots</h3>

<!-- Parking Slots Filters -->
<div class="col-12">
    <div class="filter-wrapper">
        <div class="mb-3">
            <form id="slotFilterForm" class="form-row">
                <div class="col-sm-3">
                    <input type="text" id="filterSlotID" class="form-control"
                        placeholder="Filter Slot ID">
                </div>
                <div class="col-sm-3">
                    <input type="text" id="filterSlotArea" class="form-control"
                        placeholder="Filter Area">
                </div>
                <div class="col-sm-3">
                    <select id="filterSlotStatus" class="form-control">
                        <option value="">All Status</option>
                        <option value="occupied">Occupied</option>
                        <option value="available">Available</option>
                    </select>
                </div>
                <div class="col-sm-3">
                    <button type="button" id="clearSlotFilter" class="btn btn-secondary btn-block">Clear</button>
                </div>
            </form>
        </div>
    </div>
</div>

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

<!-- RFID Cards Filters -->
<div class="col-12">
    <div class="filter-wrapper">
        <div class="mb-3">
            <form id="rfidFilterForm" class="form-row">
                <div class="col-sm-3">
                    <input type="text" id="filterRFIDCode" class="form-control"
                        placeholder="Filter RFID">
                </div>
                <div class="col-sm-3">
                    <input type="text" id="filterRFIDOwner" class="form-control"
                        placeholder="Filter Owner">
                </div>
                <div class="col-sm-3">
                    <input type="text" id="filterRFIDPlate" class="form-control"
                        placeholder="Filter Plate">
                </div>
                <div class="col-sm-3">
                    <button type="button" id="clearRfidFilter" class="btn btn-secondary btn-block">Clear</button>
                </div>
            </form>
        </div>
    </div>
</div>

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

<!-- Payment Verification Filters -->
<div class="col-12">
    <div class="filter-wrapper">
        <div class="mb-3">
            <form id="paymentFilterForm" class="form-row">
                <div class="col-sm-5">
                    <input type="text" id="filterPaymentRFID" class="form-control"
                        placeholder="Filter RFID">
                </div>
                <div class="col-sm-4">
                    <select id="filterPaymentStatus" class="form-control">
                        <option value="">All Status</option>
                        <option value="pending">Pending</option>
                        <option value="paid">Paid</option>
                    </select>
                </div>
                <div class="col-sm-3">
                    <button type="button" id="clearPaymentFilter"
                        class="btn btn-secondary btn-block">Clear</button>
                </div>
            </form>
        </div>
    </div>
</div>

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
        <button id="togglePaymentBtn" class="btn btn-primary"
            style="display:none; margin-top: 10px; margin-bottom: 20px;">
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
        let filtered = allHistory;

        const slot = document.getElementById("filterHistorySlot").value.toLowerCase().trim();
        const rfid = document.getElementById("filterHistoryRFID").value.toLowerCase().trim();
        const plate = document.getElementById("filterHistoryPlate").value.toLowerCase().trim();
        const status = document.getElementById("filterHistoryStatus").value;

        if (slot) {
            filtered = filtered.filter(row => String(row.SlotID).toLowerCase().includes(slot));
        }
        if (rfid) {
            filtered = filtered.filter(row => String(row.RFID).toLowerCase().includes(rfid));
        }
        if (plate) {
            filtered = filtered.filter(row => String(row.PlateNumberEntry ?? '').toLowerCase().includes(plate));
        }
        if (status) {
            if (status === "active") {
                filtered = filtered.filter(row => !row.TimeOut);
            } else if (status === "completed") {
                filtered = filtered.filter(row => row.TimeOut);
            }
        }

        let html = "";
        const items = historyExpanded ? filtered : filtered.slice(0, HISTORY_LIMIT);
        items.forEach(row => {
            let forceCheckoutBtn = "";
            if (!row.TimeOut) {
                forceCheckoutBtn = `
                    <button class="btn btn-sm btn-danger ml-1"
                            onclick="forceCheckout(${row.HistoryID}); event.stopPropagation();">
                        Checkout
                    </button>
                `;
            }
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
                    ${forceCheckoutBtn}
                </td>
            </tr>`;
        });
        document.getElementById("parkingHistoryBody").innerHTML = html;
        const btn = document.getElementById("toggleHistoryBtn");
        if (filtered.length > HISTORY_LIMIT) {
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

    document.getElementById("filterHistorySlot").addEventListener("input", renderHistory);
    document.getElementById("filterHistoryRFID").addEventListener("input", renderHistory);
    document.getElementById("filterHistoryPlate").addEventListener("input", renderHistory);
    document.getElementById("filterHistoryStatus").addEventListener("change", renderHistory);
    document.getElementById("clearHistoryFilter").addEventListener("click", () => {
        document.getElementById("historyFilterForm").reset();
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

    async function forceCheckout(historyID) {
        if (!confirm("Are you sure you want to force checkout this vehicle?")) {
            return;
        }
        try {
            const response = await fetch('services/force_checkout.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `history_id=${historyID}`
            });
            const res = await response.json();
            if (res.success) {
                alert(res.message || "Force checkout successful.");
                loadParkingHistory();
            } else {
                alert("Error: " + (res.message || "Unknown error"));
            }
        } catch (err) {
            console.error(err);
            alert("Failed to communicate with server.");
        }
    }

    function renderImage(src) {
        if (!src) return "<p>-</p>";
        return `<img src="${src}" class="img-fluid mb-2" style="max-width:100%">`;
    }

    document.addEventListener("DOMContentLoaded", loadParkingHistory);
</script>

<script>
    function openPayment(historyID, rfid, fee) {

        if (!fee || fee == 0) {

            alert("Vehicle has not checked out yet.");

            return;
        }

        const bank = "stb";
        const account = "057419009999";
        const name = "PHAM NGUYEN BAO TRANG";

        const qr = `https://img.vietqr.io/image/${bank}-${account}-compact.png?amount=${fee}&addInfo=PAY${historyID}&accountName=${name}`;

        document.getElementById("qr-image").src = qr;

        document.getElementById("qr-info").innerHTML =
            "RFID: " + rfid + " | Amount: " + fee + " VND";

        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth"
        });
    }
</script>

<script>
    let allPayments = [];
    let paymentExpanded = false;
    const PAYMENT_LIMIT = 5;

    async function loadPayments() {
        const res = await fetch("/Smart-Parking-Project/SmartParkingSystem/services/get_payments.php");
        allPayments = await res.json();
        renderPayments();
    }

    function renderPayments() {
        let filtered = allPayments;

        const rfid = document.getElementById("filterPaymentRFID").value.toLowerCase().trim();
        const status = document.getElementById("filterPaymentStatus").value;

        if (rfid) {
            filtered = filtered.filter(p => String(p.RFID).toLowerCase().includes(rfid));
        }
        if (status) {
            filtered = filtered.filter(p => p.Status === status);
        }

        const body = document.getElementById("paymentBody");
        let html = "";
        const items = paymentExpanded ? filtered : filtered.slice(0, PAYMENT_LIMIT);
        items.forEach(p => {
            let btn = "";
            if (p.Status == "pending") {
                btn = `<button onclick="showQR(${p.PaymentID},${p.Amount})" class="btn btn-info btn-sm">QR</button>`;
            } else {
                btn = `<span style="color:lightgreen">Paid</span>`;
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
        if (filtered.length > PAYMENT_LIMIT) {
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

    document.getElementById("filterPaymentRFID").addEventListener("input", renderPayments);
    document.getElementById("filterPaymentStatus").addEventListener("change", renderPayments);
    document.getElementById("clearPaymentFilter").addEventListener("click", () => {
        document.getElementById("paymentFilterForm").reset();
        renderPayments();
    });

    setInterval(loadPayments, 3000);
    loadPayments();

    function showQR(id, amount) {
        const bank = "stb";
        const account = "057419009999";
        const name = "PHAM NGUYEN BAO TRANG";
        const qr = `https://img.vietqr.io/image/${bank}-${account}-compact.png?amount=${amount}&addInfo=PAY${id}&accountName=${name}`;

        document.getElementById("qr-image").src = qr;
        document.getElementById("qr-info").innerHTML =
            "Payment ID: " + id + " | Amount: " + amount + " VND";
    }

    async function autoShowQR() {
        const res = await fetch("services/get_latest_payment.php");
        const p = await res.json();
        if (!p) return;
        showQR(p.PaymentID, p.Amount);
    }
    setInterval(autoShowQR, 3000);
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
        let filtered = allSlots;

        const slotId = document.getElementById("filterSlotID").value.toLowerCase().trim();
        const area = document.getElementById("filterSlotArea").value.toLowerCase().trim();
        const status = document.getElementById("filterSlotStatus").value;

        if (slotId) {
            filtered = filtered.filter(s => String(s.SlotID).toLowerCase().includes(slotId));
        }
        if (area) {
            filtered = filtered.filter(s => String(s.Area).toLowerCase().includes(area));
        }
        if (status) {
            if (status === "occupied") {
                filtered = filtered.filter(s => s.Status == 1);
            } else if (status === "available") {
                filtered = filtered.filter(s => s.Status == 0);
            }
        }

        const tbody = document.getElementById("slotBody");
        tbody.innerHTML = "";

        const slotsToShow = expanded
            ? filtered
            : filtered.slice(0, SHOW_LIMIT);

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
        if (filtered.length > SHOW_LIMIT) {
            btn.style.display = "inline-block";
            btn.textContent = expanded ? "Show Less" : "Show More";
        } else {
            btn.style.display = "none";
        }
    }

    document.getElementById("toggleSlotBtn").addEventListener("click", () => {
        expanded = !expanded;
        renderSlots();
    });

    document.getElementById("filterSlotID").addEventListener("input", renderSlots);
    document.getElementById("filterSlotArea").addEventListener("input", renderSlots);
    document.getElementById("filterSlotStatus").addEventListener("change", renderSlots);
    document.getElementById("clearSlotFilter").addEventListener("click", () => {
        document.getElementById("slotFilterForm").reset();
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
        let filtered = allRfid;

        const rfid = document.getElementById("filterRFIDCode").value.toLowerCase().trim();
        const owner = document.getElementById("filterRFIDOwner").value.toLowerCase().trim();
        const plate = document.getElementById("filterRFIDPlate").value.toLowerCase().trim();

        if (rfid) {
            filtered = filtered.filter(c => String(c.RFID).toLowerCase().includes(rfid));
        }
        if (owner) {
            filtered = filtered.filter(c => String(c.OwnerName).toLowerCase().includes(owner));
        }
        if (plate) {
            filtered = filtered.filter(c => String(c.VehiclePlate).toLowerCase().includes(plate));
        }

        let html = "";
        const items = rfidExpanded ? filtered : filtered.slice(0, RFID_LIMIT);
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
        if (filtered.length > RFID_LIMIT) {
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

    document.getElementById("filterRFIDCode").addEventListener("input", renderRfid);
    document.getElementById("filterRFIDOwner").addEventListener("input", renderRfid);
    document.getElementById("filterRFIDPlate").addEventListener("input", renderRfid);
    document.getElementById("clearRfidFilter").addEventListener("click", () => {
        document.getElementById("rfidFilterForm").reset();
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