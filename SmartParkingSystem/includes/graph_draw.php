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
        <button id="toggleHistoryBtn" class="btn btn-primary" style="display:none">
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
        <button id="toggleSlotBtn" class="btn btn-primary" style="display:none">
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
</div>

<script>
    let allHistory = [];
    let historyExpanded = false;
    const HISTORY_LIMIT = 6;

    async function loadParkingHistory() {
        const res = await fetch('http://localhost:5000/api/parkinghistory');
        allHistory = await res.json();
        renderHistory();
    }

    function renderHistory() {
        const tbody = document.getElementById("parkingHistoryBody");
        tbody.innerHTML = "";

        const historyToShow = historyExpanded
            ? allHistory
            : allHistory.slice(0, HISTORY_LIMIT);

        historyToShow.forEach(row => {
            tbody.innerHTML += `
        <tr>
            <td>${row.SlotID}</td>
            <td>${row.RFID}</td>
            <td>${row.PlateNumberEntry ?? '-'}</td>
            <td>${row.TimeIn}</td>
            <td>${row.TimeOut ?? '-'}</td>
            <td>${row.Duration ?? '-'}</td>
            <td>${row.Fee ?? '0.00'}</td>
            <td>
                <button class="btn btn-sm btn-info"
                        onclick="showDetail(${row.HistoryID})">
                    Detail
                </button>
            </td>
        </tr>`;
        });

        const btn = document.getElementById("toggleHistoryBtn");

        if (allHistory.length > HISTORY_LIMIT) {
            btn.style.display = "inline-block";
            btn.textContent = historyExpanded ? "Show Less" : "Show More";
        }
    }

    document.getElementById("toggleHistoryBtn").addEventListener("click", () => {
        historyExpanded = !historyExpanded;
        renderHistory();
    });

    document.addEventListener("DOMContentLoaded", loadParkingHistory);
</script>

<script>
    let allSlots = [];
    let expanded = false;
    const SHOW_LIMIT = 6;

    async function loadParkingSlots() {
        const res = await fetch("http://localhost:5000/api/parkingslot");
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
    fetch("http://localhost:5000/api/rfidcard")
        .then(res => res.json())
        .then(data => {
            let html = "";
            data.forEach(c => {
                html += `
        <tr>
            <td>${c.RFID}</td>
            <td>${c.OwnerName}</td>
            <td>${c.VehiclePlate}</td>
            <td>${c.Type}</td>
        </tr>`;
            });
            document.getElementById("rfidBody").innerHTML = html;
        });
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