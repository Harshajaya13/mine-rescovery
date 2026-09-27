import sys
content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mine Rescue Rover - Surface Control</title>
    <!-- Premium Minimalist Typography -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-base: #09090b; /* Zinc 950 */
            --panel-bg: #18181b; /* Zinc 900 */
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-main: #f97316; /* Industrial Orange */
            --accent-hover: #ea580c;
            --text-main: #fafafa;
            --text-muted: #a1a1aa; /* Zinc 400 */
            
            --status-safe: #22c55e;
            --status-warn: #f59e0b;
            --status-crit: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            display: grid;
            grid-template-rows: auto 1fr;
            -webkit-font-smoothing: antialiased;
        }

        header {
            padding: 1.2rem 3rem;
            background: var(--bg-base);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        header h1 {
            font-size: 1.1rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        header h1::before {
            content: '';
            display: block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-main);
        }

        .header-controls {
            display: flex;
            gap: 15px;
            align-items: center;
        }

        .status-badge {
            padding: 0.4rem 1.2rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            background: rgba(34, 197, 94, 0.1);
            color: var(--status-safe);
            letter-spacing: 0.5px;
            border: 1px solid rgba(34, 197, 94, 0.2);
            transition: all 0.3s ease;
        }

        .toggle-btn {
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 0.4rem 1.2rem;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
        }

        .toggle-btn.active {
            background: var(--accent-main);
            color: #fff;
            border-color: var(--accent-hover);
        }

        .container {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 1.5rem;
            padding: 2rem 3rem;
            max-width: 1800px;
            margin: 0 auto;
            width: 100%;
        }

        /* Sleek Panels */
        .panel {
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
            position: relative;
        }

        h2 {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Video Feed */
        .video-container {
            width: 100%;
            aspect-ratio: 16/9;
            background: #000;
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            position: relative;
        }

        .video-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        /* Metrics Grid */
        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
        }

        .metric-card {
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .metric-label {
            color: var(--text-muted);
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.4rem;
            font-weight: 600;
            margin-top: 0.5rem;
            color: var(--text-main);
        }

        /* Chart Canvas */
        .chart-container {
            width: 100%;
            height: 200px;
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
        }

        /* AI Logs Table */
        .events-table-wrapper {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            background: var(--bg-base);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
        }

        th, td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background: rgba(255,255,255,0.02);
            color: var(--text-muted);
            position: sticky;
            top: 0;
            font-weight: 600;
        }

        td {
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* Map Grid */
        .mine-map {
            display: grid;
            gap: 2px;
            background: var(--border-color);
            padding: 2px;
            border-radius: 6px;
        }

        .map-cell {
            aspect-ratio: 1;
            background: var(--panel-bg);
            border-radius: 2px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
        }

        .cell-safe { background: rgba(34, 197, 94, 0.1); }
        .cell-hazard { background: rgba(239, 68, 68, 0.15); }
        .cell-path { background: rgba(255, 255, 255, 0.05); } /* Traveled path */
        
        .cell-rover { 
            background: var(--accent-main); 
            color: #fff; 
            font-weight: 600;
            border-radius: 50%;
            transform: scale(0.8);
        }

        /* Professional Controls */
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-top: 0.5rem;
        }

        .controls-grid button {
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 1rem;
            border-radius: 6px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .controls-grid button:hover:not(:disabled) {
            background: var(--text-main);
            color: var(--bg-base);
        }

        .controls-grid button:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        
        .controls-grid button:active:not(:disabled) {
            transform: scale(0.97);
        }

        .btn-up { grid-column: 2; }
        .btn-left { grid-column: 1; grid-row: 2; }
        .btn-stop { 
            grid-column: 2; grid-row: 2; 
            background: var(--status-crit) !important;
            border-color: var(--status-crit) !important;
            color: #fff !important;
        }
        .btn-stop:hover:not(:disabled) {
            opacity: 0.9;
        }
        .btn-right { grid-column: 3; grid-row: 2; }
        .btn-down { grid-column: 2; grid-row: 3; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    </style>
</head>
<body>

    <header>
        <h1>SYS.OP // SURFACE CONTROL</h1>
        <div class="header-controls">
            <button id="autoToggleBtn" class="toggle-btn" onclick="toggleAutoMode()">MANUAL MODE</button>
            <div class="status-badge" id="system-status">SYSTEM NORMAL</div>
        </div>
    </header>

    <div class="container">
        <!-- Main Content (Left) -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            
            <!-- Video and Telemetry row -->
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem;">
                <div class="panel">
                    <h2>Live Camera Feed (YOLOv8)</h2>
                    <div class="video-container">
                        <img src="/video_feed" alt="Camera Feed">
                    </div>
                </div>

                <div class="panel">
                    <h2>Sensors & AI State</h2>
                    <div class="telemetry-grid" style="grid-template-columns: 1fr;">
                        <div class="metric-card">
                            <span class="metric-label">GAS (MQ-6)</span>
                            <span class="metric-value" id="gas-val" style="color: var(--status-safe)">SAFE</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">OBSTACLE DIST</span>
                            <span class="metric-value" id="dist-val">-- cm</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">SIGNAL RSSI</span>
                            <span class="metric-value" id="rssi-val">-- dBm</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">AI ACTION</span>
                            <span class="metric-value" id="action-val" style="font-size: 1.1rem; color: var(--accent-main)">--</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sensor History Graph -->
            <div class="panel">
                <h2>Sensor Telemetry History</h2>
                <div class="chart-container">
                    <canvas id="sensorChart"></canvas>
                </div>
            </div>

            <!-- AI Detection Log Table -->
            <div class="panel">
                <h2>AI Detection & Action Log</h2>
                <div class="events-table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>TIME</th>
                                <th>TRIGGER</th>
                                <th>DETECTED</th>
                                <th>AI DECISION</th>
                            </tr>
                        </thead>
                        <tbody id="events-table-body">
                            <!-- JS populated -->
                        </tbody>
                    </table>
                </div>
            </div>

        </div>

        <!-- Sidebar (Right) -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
            
            <!-- Map Panel -->
            <div class="panel">
                <h2>Mine Section Map</h2>
                <div class="mine-map" id="mine-map">
                    <!-- JS will populate grid -->
                </div>
            </div>

            <!-- Manual Override Panel -->
            <div class="panel" id="manual-panel">
                <h2>Manual Override</h2>
                <div class="controls-grid">
                    <button class="btn-up" onclick="sendCommand('forward')">W</button>
                    <button class="btn-left" onclick="sendCommand('left')">A</button>
                    <button class="btn-stop" onclick="sendCommand('stop')">STOP</button>
                    <button class="btn-right" onclick="sendCommand('right')">D</button>
                    <button class="btn-down" onclick="sendCommand('backward')">S</button>
                </div>
            </div>

        </div>
    </div>

    <script>
        const socket = io();

        // State variables
        let isAutoMode = false;
        let pastPaths = new Set(); // store "x,y" of everywhere the rover goes

        // Setup Chart.js
        const ctx = document.getElementById('sensorChart').getContext('2d');
        const sensorChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Distance (cm)',
                        borderColor: '#f97316',
                        data: [],
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    },
                    {
                        label: 'Signal (dBm)',
                        borderColor: '#a1a1aa',
                        data: [],
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: { display: false },
                    y: { 
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#a1a1aa', font: { family: 'JetBrains Mono' } }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#fafafa', font: { family: 'Inter' } } }
                }
            }
        });

        // Toggle Auto Mode
        function toggleAutoMode() {
            fetch('/toggle_mode', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                isAutoMode = data.auto_mode;
                const btn = document.getElementById('autoToggleBtn');
                const manualPanel = document.getElementById('manual-panel');
                
                if(isAutoMode) {
                    btn.classList.add('active');
                    btn.innerText = 'AUTONOMOUS ACTIVE';
                    manualPanel.style.opacity = '0.4';
                    // disable buttons
                    manualPanel.querySelectorAll('button').forEach(b => b.disabled = true);
                } else {
                    btn.classList.remove('active');
                    btn.innerText = 'MANUAL MODE';
                    manualPanel.style.opacity = '1';
                    manualPanel.querySelectorAll('button').forEach(b => b.disabled = false);
                }
            });
        }

        // Send command to server
        function sendCommand(action) {
            if(isAutoMode) return; // Block manual commands if in auto
            fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: action })
            });
        }

        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if(isAutoMode) return;
            if(e.key === 'w' || e.key === 'W') sendCommand('forward');
            if(e.key === 's' || e.key === 'S') sendCommand('backward');
            if(e.key === 'a' || e.key === 'A') sendCommand('left');
            if(e.key === 'd' || e.key === 'D') sendCommand('right');
            if(e.key === ' ') sendCommand('stop');
        });

        // Listen for telemetry
        socket.on('telemetry_update', (data) => {
            const sensor = data.sensor;
            const ai = data.ai_report;
            const map = data.map;
            
            // Sync auto mode state just in case
            if (data.auto_mode !== isAutoMode) {
                isAutoMode = data.auto_mode;
            }

            // Update Metrics
            document.getElementById('dist-val').innerText = sensor.distance_cm + ' cm';
            document.getElementById('rssi-val').innerText = sensor.rssi + ' dBm';
            
            const gasElem = document.getElementById('gas-val');
            if (sensor.gas_detected === 1) {
                gasElem.innerText = 'DETECTED';
                gasElem.style.color = 'var(--status-crit)';
            } else {
                gasElem.innerText = 'SAFE';
                gasElem.style.color = 'var(--status-safe)';
            }

            // Update AI State
            document.getElementById('action-val').innerText = ai.suggested_action.toUpperCase();
            
            const statusBadge = document.getElementById('system-status');
            statusBadge.innerText = ai.status;
            if(ai.status === 'CRITICAL' || ai.status === 'ALERT') {
                statusBadge.style.background = 'var(--status-crit)';
                statusBadge.style.color = '#fff';
            } else if (ai.status === 'WARNING') {
                statusBadge.style.background = 'var(--status-warn)';
                statusBadge.style.color = '#fff';
            } else {
                statusBadge.style.background = 'rgba(34, 197, 94, 0.1)';
                statusBadge.style.color = 'var(--status-safe)';
            }

            // Update Chart
            const timeNow = new Date().toLocaleTimeString();
            sensorChart.data.labels.push(timeNow);
            sensorChart.data.datasets[0].data.push(sensor.distance_cm);
            sensorChart.data.datasets[1].data.push(sensor.rssi);
            
            if(sensorChart.data.labels.length > 30) { // Keep last 30 points
                sensorChart.data.labels.shift();
                sensorChart.data.datasets[0].data.shift();
                sensorChart.data.datasets[1].data.shift();
            }
            sensorChart.update();

            // Update AI Logs Table
            if(ai.event) {
                const tbody = document.getElementById('events-table-body');
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${timeNow}</td>
                    <td>${ai.event.trigger}</td>
                    <td style="color: var(--accent-main); font-weight: 600;">${ai.event.detected}</td>
                    <td>${ai.event.action}</td>
                `;
                tbody.prepend(row); // Add to top
                
                // limit table rows to 20
                if (tbody.children.length > 20) {
                    tbody.removeChild(tbody.lastChild);
                }
            }

            // Update Paths Set
            pastPaths.add(`${map.rover_pos[0]},${map.rover_pos[1]}`);

            // Render Map
            renderMap(map.grid, map.rover_pos, map.facing);
        });

        function renderMap(gridData, roverPos, facing) {
            const mapContainer = document.getElementById('mine-map');
            const size = gridData.length;
            mapContainer.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
            mapContainer.innerHTML = '';

            for (let y = size - 1; y >= 0; y--) { // Y=0 is bottom
                for (let x = 0; x < size; x++) {
                    const cell = document.createElement('div');
                    cell.className = 'map-cell';
                    
                    const val = gridData[y][x];
                    if (val === 1) cell.classList.add('cell-safe');
                    else if (val === 2) cell.classList.add('cell-hazard');
                    
                    // Add path trail
                    if (pastPaths.has(`${x},${y}`) && !(x === roverPos[0] && y === roverPos[1])) {
                        cell.classList.add('cell-path');
                    }

                    if (x === roverPos[0] && y === roverPos[1]) {
                        cell.classList.add('cell-rover');
                        // Add facing arrow
                        if(facing === 'N') cell.innerHTML = '↑';
                        if(facing === 'S') cell.innerHTML = '↓';
                        if(facing === 'E') cell.innerHTML = '→';
                        if(facing === 'W') cell.innerHTML = '←';
                    }

                    mapContainer.appendChild(cell);
                }
            }
        }
    </script>
</body>
</html>
"""
with open("/home/harsha/test/mine_rescue_rover/laptop_server/dashboard/templates/index.html", "w") as f:
    f.write(content)
