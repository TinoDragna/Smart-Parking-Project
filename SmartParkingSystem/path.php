<?php
session_start();

if ($_SESSION['LoginInto'] == "TRUE") {
    $current = 'path';
    require_once("includes/header.php");
} else {
    header('Location: /Smart-Parking-Project/SmartParkingSystem/login.php');
}
?>

<div class="wrap" style="background: url(image/3.jpg); padding-top: 10px; padding-bottom: 10px;">
    <div class="col-sm-12">
        <h2 class="sub-1" style="text-align: center;">
            TOTAL AVAILABLE SLOTS: <span id="available-count">0</span>
        </h2>
    </div>
    <button id="test-path" style="margin:20px;">TEST PATH</button>
    <div class="col-sm-12" style="display: flex; justify-content: center;">
        <div class="parking-area"
            style="border: 2px solid #ccc; padding: 10px; border-radius: 10px; background: #fff; display: inline-block; margin: 20px auto;">
            <div id="slot-container" style="
                    position: relative;
                    width: 1200px;
                    height: 600px;
                    border: 2px solid #ccc;
                    margin: 20px auto;
                    padding: 0;
                    box-sizing: border-box;
                ">
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
    const slotContainer = document.getElementById("slot-container");
    // Add some spacing for path lines
    // ===== GLOBAL layout values =====
    let slotWidth = 0;
    let slotHeight = 0;
    let hSpacing = 20;
    let vSpacing = 20;
    let maxCol = 0;
    let maxRow = 0;
    async function fetchSlotsFromDB() {
        try {
            // Lấy danh sách tất cả slot
            const slotsRes = await fetch('services/get_slot.php');
            const slots = await slotsRes.json(); // ["A1", "A2", ...]
            console.log("Slots from DB:", slots);

            // Lấy danh sách slot bị occupied
            const occupiedRes = await fetch('services/get_occupied.php');
            const occupiedSlots = await occupiedRes.json(); // ["A2", "B3", ...]

            let availableCount = 0;

            slotContainer.innerHTML = ''; // clear previous

            // Determine grid size
            maxCol = 0, maxRow = 0;
            slots.forEach(slot => {
                if (slot.coordinates.col > maxCol) maxCol = slot.coordinates.col;
                if (slot.coordinates.row > maxRow) maxRow = slot.coordinates.row;
            });

            maxCol += 1; // cols count
            maxRow += 1; // rows count

            const slotContainerWidth = slotContainer.clientWidth;
            const slotContainerHeight = slotContainer.clientHeight;

            slotWidth = (slotContainerWidth - hSpacing * (maxCol + 1)) / maxCol;
            slotHeight = (slotContainerHeight - vSpacing * (maxRow + 1)) / maxRow;

            slots.forEach(slot => {
                const x = hSpacing + slot.coordinates.col * (slotWidth + hSpacing);
                const y = vSpacing + slot.coordinates.row * (slotHeight + vSpacing);

                // Entry/Exit symbols
                // Entry/Exit arrow
                // Entry / Exit arrow (slot-centered)
                if (slot.SlotName === "Entry" || slot.SlotName === "Exit") {
                    const el = document.createElement('div');

                    el.style.position = 'absolute';
                    el.style.left = `${x}px`;
                    el.style.top = `${y}px`;
                    el.style.width = `${slotWidth}px`;
                    el.style.height = `${slotHeight}px`;

                    el.style.display = 'flex';
                    el.style.justifyContent = 'center';
                    el.style.alignItems = 'center';

                    el.style.fontSize = '60px';
                    el.style.lineHeight = '1';
                    el.style.userSelect = 'none';
                    el.style.pointerEvents = 'none';

                    el.style.color =
                        slot.SlotName === "Entry" ? 'blue' : 'orange';

                    const dirMap = {
                        N: '↑',
                        S: '↓',
                        E: '→',
                        W: '←'
                    };

                    el.innerText = dirMap[slot.Direction] || '→';

                    console.log(slot.Direction);

                    slotContainer.appendChild(el);
                    return;
                }



                // Normal slot box
                const el = document.createElement('div');
                el.className = 'slot';
                el.id = `slot-${slot.SlotName}`;
                el.style.position = 'absolute';
                el.style.left = `${x}px`;
                el.style.top = `${y}px`;
                el.style.width = `${slotWidth}px`;
                el.style.height = `${slotHeight}px`;
                el.style.border = '1px solid #ccc';
                el.style.borderRadius = '8px';
                el.style.display = 'flex';
                el.style.flexDirection = 'column';
                el.style.justifyContent = 'center';
                el.style.alignItems = 'center';
                el.style.textAlign = 'center';
                el.style.boxSizing = 'border-box';

                // Color based on status
                if (slot.Status == 1) {
                    el.style.background = 'rgb(255, 204, 204)'; // occupied = red
                } else if (slot.Status == 2) {
                    el.style.background = 'rgb(255, 255, 204)'; // reserved = yellow
                }
                else {
                    el.style.background = 'rgb(204, 255, 204)'; // available = green
                    availableCount += 1;
                }

                const h4 = document.createElement('h4');
                h4.style.margin = '0';
                h4.style.fontSize = '14px';
                h4.innerText = slot.SlotName;
                el.appendChild(h4);

                const p = document.createElement('p');
                p.style.margin = '0';
                p.style.fontSize = '12px';
                if (slot.Status == 0) {
                    p.innerHTML = `Status: <strong style="color:green">Available</strong>`;
                } else if (slot.Status == 1) {
                    p.innerHTML = `Status: <strong style="color:red">Occupied</strong>`;
                } else if (slot.Status == 2) {
                    p.innerHTML = `Status: <strong style="color:orange">Reserved</strong>`;
                }
                el.appendChild(p);

                slotContainer.appendChild(el);
            });

            // Hiển thị số slot trống
            document.getElementById("available-count").textContent = availableCount;
        } catch (error) {
            console.error("Lỗi lấy slot từ DB:", error);
        }
    }
    function createPathLayer() {
        let svg = document.getElementById("path-layer");
        if (svg) svg.remove();

        svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("id", "path-layer");
        svg.style.position = "absolute";
        svg.style.left = "0";
        svg.style.top = "0";
        svg.style.width = "100%";
        svg.style.height = "100%";
        svg.style.pointerEvents = "none";
        svg.style.zIndex = "5";

        slotContainer.appendChild(svg);
        return svg;
    }

    function createMarkerLayer() {
        let layer = document.getElementById("marker-layer");
        if (layer) layer.remove();

        layer = document.createElement("div");
        layer.id = "marker-layer";
        layer.style.position = "absolute";
        layer.style.left = "0";
        layer.style.top = "0";
        layer.style.width = "100%";
        layer.style.height = "100%";
        layer.style.pointerEvents = "none";
        layer.style.zIndex = "10";

        slotContainer.appendChild(layer);
        return layer;
    }

    function drawYouAreHere(node) {
        const layer = createMarkerLayer();

        const x = hSpacing + node.col * (slotWidth + hSpacing) + slotWidth / 2;
        const y = vSpacing + node.row * (slotHeight + vSpacing) + slotHeight / 2;

        const marker = document.createElement("div");
        marker.style.position = "absolute";
        marker.style.left = `${x}px`;
        marker.style.top = `${y}px`;
        marker.style.transform = "translate(-50%, -70%)";
        marker.style.display = "flex";
        marker.style.flexDirection = "column";
        marker.style.alignItems = "center";
        marker.style.justifyContent = "center";

        // Dot
        const car = document.createElement("div");
        car.innerText = "🚗";
        car.style.fontSize = "60px";
        car.style.lineHeight = "1";

        // Label
        // const label = document.createElement("div");
        // label.innerText = "YOU ARE HERE";
        // label.style.fontSize = "12px";
        // label.style.fontWeight = "bold";
        // label.style.color = "blue";
        // label.style.background = "white";
        // label.style.padding = "2px 6px";
        // label.style.borderRadius = "6px";
        // label.style.marginBottom = "4px";
        // label.style.boxShadow = "0 2px 4px rgba(0,0,0,0.2)";

        marker.appendChild(car);
        layer.appendChild(marker);
    }

    // function getNodeAnchor(node, isEndpoint = false, direction = null) {
    // 	let x = hSpacing + node.col * (slotWidth + hSpacing) + slotWidth / 2;
    // 	let y = vSpacing + node.row * (slotHeight + vSpacing) + slotHeight / 2;

    // 	if (isEndpoint && direction) {
    // 		switch (direction) {
    // 			case 'N': y -= slotHeight / 2; break;
    // 			case 'S': y += slotHeight / 2; break;
    // 			case 'W': x -= slotWidth / 2; break;
    // 			case 'E': x += slotWidth / 2; break;
    // 		}
    // 	}

    // 	return { x, y };
    // }


    function drawPath(pathDetails) {
        pathNodes = pathDetails.pathNodes;
        const type = pathDetails.type; // "entry" or "exit"
        let color;
        switch (type) {
            case "entry":
                color = "blue";
                break;
            case "exit":
                color = "orange";
                break;
            default:
                color = "black";
        }
        const svg = createPathLayer();
        svg.innerHTML = '';

        if (!pathNodes || pathNodes.length < 2) return;

        drawYouAreHere(pathNodes[0]);

        const toPixel = (node) => ({
            x: hSpacing + node.col * (slotWidth + hSpacing) + slotWidth / 2,
            y: vSpacing + node.row * (slotHeight + vSpacing) + slotHeight / 2
        });

        let d = '';
        pathNodes.forEach((node, i) => {
            const p = toPixel(node);
            d += (i === 0 ? 'M' : ' L') + ` ${p.x} ${p.y}`;
        });

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", d);

        path.setAttribute("stroke", color);
        path.setAttribute("stroke-width", "3.5");
        path.setAttribute("fill", "none");
        path.setAttribute("stroke-linecap", "round");
        path.setAttribute("stroke-linejoin", "round");

        svg.appendChild(path);
    }

    document.getElementById("test-path").addEventListener("click", () => {
        const entryToA5 = {
            "pathNodes": [
                { col: 0, row: 5 },   // Entry road
                { col: 0, row: 4.5 },
                { col: 0.5, row: 4.5 },
                { col: 0.5, row: 3.5 },
                { col: 0.5, row: 2.5 },
                { col: 0.5, row: 1.5 },
                { col: 0.5, row: 0.5 },
                { col: 0.5, row: 0 },
                { col: 1, row: 0 }
            ],
            "type": "entry"
        };

        const A5ToExit = {
            "pathNodes": [
                { col: 1, row: 0 },
                { col: 1, row: -0.5 },
                { col: 2, row: -0.5 },
                { col: 3, row: -0.5 },
                { col: 4, row: -0.5 },
                { col: 4.5, row: -0.5 },
                { col: 4.5, row: 0.5 },
                { col: 4.5, row: 5 },
                { col: 5, row: 5 }
            ],
            "type": "exit"
        };

        chosenPath = entryToA5;
        // chosenPath = A5ToExit;

        drawPath(chosenPath);
    });

    // Gọi hàm khi load trang
    fetchSlotsFromDB();
</script>

<script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>

<script>
    let client;

    function initMQTT() {
        // CHANGE to your broker WSS endpoint
        // Example: wss://broker.example.com:8084/mqtt
        client = mqtt.connect("ws://172.16.2.4:9001/mqtt", {
            keepalive: 60,
            clean: true,
            reconnectPeriod: 3000,
            connectTimeout: 4000,
        });

        client.on("connect", () => {
            console.log("✅ MQTT connected over WSS");

            // Subscribe to topics
            client.subscribe("map/path");
            client.subscribe("car/position");
        });

        client.on("message", (topic, message) => {
            try {
                const data = JSON.parse(message.toString());
                console.log("MQTT message:", topic, data);

                if (topic === "map/path") {
                    drawPath(data);
                }
            } catch (e) {
                console.error("Invalid MQTT message", e);
            }
        });

        client.on("error", (err) => {
            console.error("❌ MQTT error", err);
        });

        client.on("close", () => {
            console.warn("⚠️ MQTT disconnected");
        });
    }

    // Start MQTT after page is ready
    window.addEventListener("load", initMQTT);

</script>

<?php require_once("includes/footer.php"); ?>