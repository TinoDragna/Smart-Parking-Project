<?php
require_once("session_start.php");

if ($_SESSION['LoginInto'] == "TRUE") {
    $current = 'analytics';
    require_once("includes/header.php");
} else {
    header('Location: /Smart-Parking-Project/SmartParkingSystem/login.php');
    exit();
}

require_once("php/connectSQL.php");

/* =========================
   TOTAL VEHICLES
========================= */
$sql_total = "
SELECT COUNT(*) AS TotalVehicles
FROM parkinghistory
";

$result_total = mysqli_query($conn, $sql_total);
$row_total = mysqli_fetch_assoc($result_total);
$totalVehicles = $row_total['TotalVehicles'] ?? 0;

/* =========================
   AVERAGE PARKING DURATION
========================= */

$sql_avg_duration = "
SELECT AVG(Duration) AS AvgDuration
FROM parkinghistory
WHERE Duration IS NOT NULL
";

$result_avg = mysqli_query($conn, $sql_avg_duration);

$row_avg = mysqli_fetch_assoc($result_avg);

$avgDuration = round(
    $row_avg['AvgDuration'] ?? 0,
    2
);

/* =========================
   PEAK HOUR
========================= */
$sql_peak = "
SELECT
    HOUR(TimeIn) AS Hour,
    COUNT(*) AS VehicleCount
FROM parkinghistory
GROUP BY HOUR(TimeIn)
ORDER BY VehicleCount DESC
LIMIT 1
";

$result_peak = mysqli_query($conn, $sql_peak);
$row_peak = mysqli_fetch_assoc($result_peak);

$peakHour = isset($row_peak['Hour']) ? $row_peak['Hour'] : '-';
$peakCount = isset($row_peak['VehicleCount']) ? $row_peak['VehicleCount'] : 0;

/* =========================
   LOWEST HOUR
========================= */
$sql_low = "
SELECT
    HOUR(TimeIn) AS Hour,
    COUNT(*) AS VehicleCount
FROM parkinghistory
GROUP BY HOUR(TimeIn)
ORDER BY VehicleCount ASC
LIMIT 1
";

$result_low = mysqli_query($conn, $sql_low);
$row_low = mysqli_fetch_assoc($result_low);

$lowHour = isset($row_low['Hour']) ? $row_low['Hour'] : '-';
$lowCount = isset($row_low['VehicleCount']) ? $row_low['VehicleCount'] : 0;

/* =========================
   VEHICLES PER DAY
========================= */
$sql_day = "
SELECT
    DATE(TimeIn) AS EntryDate,
    COUNT(*) AS VehicleCount
FROM parkinghistory
GROUP BY DATE(TimeIn)
ORDER BY EntryDate
";

$result_day = mysqli_query($conn, $sql_day);

$dates = [];
$dailyCounts = [];

while ($row = mysqli_fetch_assoc($result_day)) {
    $dates[] = $row['EntryDate'];
    $dailyCounts[] = $row['VehicleCount'];
}

/* =========================
   TOTAL REVENUE
========================= */

$sql_total_revenue = "
SELECT SUM(Amount) AS TotalRevenue
FROM payments
WHERE LOWER(Status)='paid'
";

$result_revenue_total =
    mysqli_query($conn, $sql_total_revenue);

$row_revenue_total =
    mysqli_fetch_assoc($result_revenue_total);

$totalRevenue =
    $row_revenue_total['TotalRevenue'] ?? 0;

/* =========================
   REVENUE PER DAY
========================= */

$sql_revenue = "
SELECT
    DATE(CreatedAt) AS RevenueDate,
    SUM(Amount) AS Revenue
FROM payments
WHERE LOWER(Status)='paid'
GROUP BY DATE(CreatedAt)
ORDER BY RevenueDate
";

$result_revenue =
    mysqli_query($conn, $sql_revenue);

$revenueDates = [];
$revenues = [];

while ($row = mysqli_fetch_assoc($result_revenue)) {

    $revenueDates[] =
        $row['RevenueDate'];

    $revenues[] =
        $row['Revenue'];

}

/* =========================
   SLOT USAGE
========================= */
$sql_slot = "
SELECT
    SlotID,
    COUNT(*) AS UsageCount
FROM parkinghistory
GROUP BY SlotID
ORDER BY SlotID
";

$result_slot = mysqli_query($conn, $sql_slot);

$slots = [];
$slotCounts = [];

while ($row = mysqli_fetch_assoc($result_slot)) {
    $slots[] = "Slot " . $row['SlotID'];
    $slotCounts[] = $row['UsageCount'];
}
?>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
    .analytics-container {
        padding: 20px;
    }

    .dashboard-cards {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        margin-bottom: 30px;
    }

    .dashboard-card {
        flex: 1;
        min-width: 250px;
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .dashboard-card h3 {
        margin-bottom: 10px;
        color: #555;
    }

    .dashboard-card .value {
        font-size: 32px;
        font-weight: bold;
        color: #007bff;
    }

    .chart-container {
        background: white;
        margin-bottom: 30px;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .chart-container h3 {
        margin-bottom: 20px;
    }

    canvas {
        max-height: 400px;
    }
</style>

<div class="wrap" style="background:#f4f6f9;">
    <div class="analytics-container">

        <h1>Smart Parking Analytics Dashboard</h1>

        <!-- CARDS -->
        <div class="dashboard-cards">

            <div class="dashboard-card">
                <h3>Total Vehicles</h3>
                <div class="value">
                    <?php echo $totalVehicles; ?>
                </div>
            </div>

            <div class="dashboard-card">
                <h3>Peak Hour</h3>
                <div class="value">
                    <?php echo is_numeric($peakHour)
                        ? sprintf("%02d:00", $peakHour)
                        : 'N/A';
                    ?>
                </div>
                <p><?php echo $peakCount; ?> vehicles</p>
            </div>

            <div class="dashboard-card">
                <h3>Lowest Hour</h3>
                <div class="value">
                    <?php echo is_numeric($lowHour)
                        ? sprintf("%02d:00", $lowHour)
                        : 'N/A';
                    ?>
                </div>
                <p><?php echo $lowCount; ?> vehicles</p>
            </div>

            <div class="dashboard-card">
                <h3>Total Revenue</h3>

                <div class="value" style="font-size:24px;">
                    <?php
                    echo number_format(
                        $totalRevenue,
                        0,
                        ',',
                        '.'
                    );
                    ?>
                    VND
                </div>
            </div>

            <div class="dashboard-card">

                <h3>Average Duration</h3>

                <div class="value">
                    <?php echo $avgDuration; ?>
                </div>

                <p>minutes</p>

            </div>
        </div>

        <!-- VEHICLES PER DAY -->
        <div class="chart-container">
            <h3>Vehicles Per Day</h3>
            <canvas id="dayChart"></canvas>
        </div>

        <div id="hourDetailContainer" class="chart-container" style="display:none;">

            <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
    ">

                <h3 id="selectedDateTitle">
                    Vehicles Per Hour
                </h3>

                <button id="closeHourChart">
                    Close
                </button>

            </div>

            <canvas id="hourChart"></canvas>

        </div>

        <div class="chart-container">
            <h3>Revenue Per Day</h3>
            <canvas id="revenueChart"></canvas>
        </div>

        <!-- SLOT USAGE -->
        <div class="chart-container">
            <h3>Slot Usage Distribution</h3>
            <canvas id="slotChart"></canvas>
        </div>

    </div>
</div>

<script>

    let hourChart = null;

    /* VEHICLES PER DAY */

    const dayChart =
        new Chart(
            document.getElementById('dayChart'),
            {
                type: 'line',

                data: {
                    labels:
                        <?php echo json_encode($dates); ?>,

                    datasets: [{
                        label: 'Vehicles',

                        data:
                            <?php echo json_encode($dailyCounts); ?>,

                        fill: false
                    }]
                }
            });

    /* CLICK DAY */

    document
        .getElementById('dayChart')
        .onclick = function (evt) {

            const points =
                dayChart.getElementsAtEventForMode(
                    evt,
                    'nearest',
                    { intersect: true },
                    true
                );

            if (points.length === 0) {
                return;
            }

            const index =
                points[0].index;

            const selectedDate =
                dayChart.data.labels[index];

            loadHourlyChart(
                selectedDate
            );
        };

    /* LOAD HOUR DATA */

    function loadHourlyChart(date) {

        fetch(
            'services/get_hourly_data.php?date='
            + encodeURIComponent(date)
        )

            .then(
                response =>
                    response.json()
            )

            .then(data => {

                document
                    .getElementById(
                        'hourDetailContainer'
                    )
                    .style.display = 'block';

                document
                    .getElementById(
                        'selectedDateTitle'
                    )
                    .innerHTML =
                    'Vehicles Per Hour - '
                    + date;

                let hours = [];
                let counts = [];

                data.forEach(row => {

                    hours.push(
                        row.Hour
                            .toString()
                            .padStart(2, '0')
                        + ':00'
                    );

                    counts.push(
                        row.VehicleCount
                    );

                });

                if (hourChart) {
                    hourChart.destroy();
                }

                hourChart =
                    new Chart(
                        document.getElementById(
                            'hourChart'
                        ),
                        {
                            type: 'bar',

                            data: {
                                labels: hours,

                                datasets: [{
                                    label: 'Vehicles',
                                    data: counts
                                }]
                            }
                        });

            });
    }

    /* CLOSE BUTTON */

    document
        .getElementById(
            'closeHourChart'
        )
        .onclick = function () {

            document
                .getElementById(
                    'hourDetailContainer'
                )
                .style.display = 'none';

        };

    /* SLOT USAGE */

    new Chart(
        document.getElementById('slotChart'),
        {
            type: 'pie',

            data: {
                labels:
                    <?php echo json_encode($slots); ?>,

                datasets: [{
                    data:
                        <?php echo json_encode($slotCounts); ?>
                }]
            }
        });

    /* REVENUE */

    new Chart(
        document.getElementById('revenueChart'),
        {
            type: 'bar',

            data: {
                labels:
                    <?php echo json_encode($revenueDates); ?>,

                datasets: [{

                    label: 'Revenue (VNĐ)',

                    data:
                        <?php echo json_encode($revenues); ?>

                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

</script>

<?php require_once("includes/footer.php"); ?>