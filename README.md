# 🔴 AI-Powered Underground Mine Safety, Monitoring & Rescue System
> **Core Identity:** SENSE. SEE. SAVE.  
> **Target Domain:** Jharkhand Underground Coal Mines Safety & Disaster Reconnaissance

---

## 📌 Executive Summary

Underground coal mining environments pose critical risks of explosive Methane ($\text{CH}_4$) accumulation, deadly Carbon Monoxide ($\text{CO}$) poisoning, oxygen depletion, structural cave-ins, and zero-visibility coal dust clouds. During disasters, sending human rescue teams in without situational awareness creates severe risks of secondary casualties.

This project delivers a **ruggedized autonomous hazard-scanning rover** paired with a **surface-level tactical mission control dashboard**. The rover enters disaster zones first, scans atmospheric hazards, locates trapped miners using AI-enhanced thermal imaging, and dynamically computes gas-avoiding rescue vectors using $A^*$ pathfinding.

---

## 🏗️ End-to-End System Architecture

```mermaid
graph TD
    subgraph UNDERGROUND_ROVER["Underground Rover Hardware (Jetson Orin Nano Layer)"]
        Sensors["Gas Array (MQ-4, CO, O2, Temp/Hum)"] -->|ADC / I2C| Jetson["NVIDIA Jetson Orin Nano"]
        LiDAR["RPLiDAR A2 (360° Laser Scanner)"] -->|USB Serial| Jetson
        FLIR["FLIR Lepton 3.5 Thermal Camera"] -->|CSI / SPI| Jetson
        HD_Cam["HD Optical Camera"] -->|USB| Jetson
        IMU["MPU-6050 IMU + Encoders"] -->|I2C| Jetson
        Jetson -->|YOLOv8 Onboard Inference| Detection["Thermal Heat Signature Detection"]
    end

    subgraph COMMS["Communication Bridge"]
        Jetson -->|5.8GHz Long-Range Mesh Radio / WebSocket| Server
    end

    subgraph SURFACE_SERVER["Surface Laptop Server (Flask Backend)"]
        Server["Flask App + Socket.IO Server"]
        Server --> ThresholdEngine["Gas Threshold Engine"]
        Server --> GridBuilder["Occupancy Grid Builder"]
        Server --> PathEngine["Dynamic A* Pathfinding Engine"]
        Server --> Blackbox["Timestamped Blackbox Logger"]
    end

    subgraph DASHBOARD["Mission Control Dashboard (Browser UI)"]
        Server -->|Socket.IO Telemetry Stream| Gauges["5 Live SVG Gas Gauges"]
        Server -->|MJPEG Feed /video_feed| VideoPanel["Dual Vision Panel (HD / Thermal)"]
        Server -->|Grid & Vector Updates| TacticalMap["Live 2D Tactical Grid Map"]
        Server -->|Alert Events| RedAlert["Full Screen Visual Red Alert"]
        TacticalMap -->|Interactive Vector| PathRender["Safe Rescue Route Overlay"]
        Blackbox -->|1-Click Export| ExportBtn["Incident Log (.txt)"]
    end
```

---

## 🔄 Real-Time Data & Event Flow

```mermaid
sequenceDiagram
    autonumber
    participant Rover as Underground Rover
    participant Server as Surface Flask Backend
    participant Dash as Mission Control UI
    participant Team as Rescue Commander

    loop Every 100ms (10Hz Telemetry Tick)
        Rover->>Server: Send Sensor Telemetry (CH4, CO, O2, Temp, Hum, Pos)
        Server->>Server: Evaluate Threshold Engine (DGMS Safety Limits)
        alt Hazard Threshold Exceeded
            Server->>Dash: Emit `hazard_alert` (Red Flash + Audio Ping)
        end
        Server->>Dash: Emit `telemetry_update` (Update SVG Gauges & Graphs)
    end

    loop Every 33ms (30 FPS Video Stream)
        Rover->>Server: Stream MJPEG Frame (HD / Thermal + YOLO Bounding Box)
        Server->>Dash: Relay `/video_feed` Stream
    end

    opt Survivor Detected by Thermal AI
        Rover->>Server: Emit `worker_detected` { coord: [x, y], confidence: 0.94 }
        Server->>Server: Run A* Pathfinding Engine (Avoid Red Hazard Cells)
        Server->>Dash: Emit `rescue_path_calculated` { path: [[x1,y1], [x2,y2]...], worker: [x,y] }
        Dash->>Dash: Pin Worker on 2D Grid + Draw Green Safe Vector
        Dash->>Team: Visual Indicator "RESCUE VECTOR READY"
    end
```

---

## 🔩 Hardware Specification & Sensor Topology

| Module | Component / Sensor | Communication Protocol | Operational Function |
|---|---|---|---|
| **Primary Compute** | NVIDIA Jetson Orin Nano (8GB) | Internal PCIe / USB 3.2 | 40 TOPS AI compute, runs YOLOv8 at 30 FPS locally |
| **Methane Sensor** | MQ-4 / Figaro TGS2611 | Analog → ADS1115 ADC (I2C) | Measures $\text{CH}_4$ volume % (DGMS Alarm threshold: 1.25%) |
| **Carbon Monoxide** | MQ-7 / Electrochemical | Analog → ADS1115 ADC (I2C) | Measures $\text{CO}$ concentration in PPM (OSHA Alarm: 25 PPM) |
| **Oxygen Cell** | Electrochemical $\text{O}_2$ Sensor | Analog → ADS1115 ADC (I2C) | Measures $\text{O}_2$ % depletion (Alert limit: < 19.5%) |
| **Climate Array** | SHT31 / DHT22 | Digital Single-Bus / I2C | Ambient Temperature (°C) & Relative Humidity (%) |
| **Thermal Camera** | FLIR Lepton 3.5 Radiometric | SPI (Video) + I2C (Control) | Detects 37°C body heat signatures through dense dust |
| **LiDAR Scanner** | RPLiDAR A2M8 (12m range) | UART → USB Serial | 360° 2D laser mapping for tunnel occupancy grid |
| **IMU / Odometry** | MPU-6050 + Optical Encoders | I2C / GPIO Interrupts | Dead-reckoning position estimation without GPS |
| **Long-Range Link** | 5.8GHz Mesh Wireless Radio | Ethernet / TCP-IP | High-throughput data tunnel between mine & surface |

---

## 💻 Software Architecture & Code Structure

### Directory Layout
```
mine_rescue_rover/
├── laptop_server/
│   ├── app.py                      # Flask backend, Socket.IO handlers, A* engine
│   └── dashboard/
│       ├── templates/
│       │   └── index.html          # Mission Control UI (CSS Glassmorphism + JS)
│       └── static/
│           ├── css/
│           └── js/
├── raspberry_pi/                   # Embedded telemetry collection daemon
├── esp32/                          # Motor controller & hardware bridge firmware
├── esp_cam/                        # Dual camera relay firmware
└── README.md                       # Master System Specification
```

---

## 🧮 Data Schemas & WebSocket API Specification

### 1. Telemetry Payload Schema (`telemetry_data`)
```json
{
  "timestamp": 1727453400.125,
  "rover_id": "ROVER_ALPHA_01",
  "position": { "x": 4.5, "y": 2.1, "heading": 180.0 },
  "sensors": {
    "ch4": { "value": 1.45, "unit": "%", "status": "CRITICAL" },
    "co": { "value": 28.5, "unit": "ppm", "status": "WARNING" },
    "o2": { "value": 19.1, "unit": "%", "status": "WARNING" },
    "temp": { "value": 36.2, "unit": "°C", "status": "NORMAL" },
    "humidity": { "value": 78.0, "unit": "%", "status": "NORMAL" }
  },
  "battery": 88,
  "signal_dbm": -62
}
```

### 2. Hazard Alert Event Schema (`hazard_alert`)
```json
{
  "alert_id": "ALT_99201",
  "type": "GAS_SPIKE_BREACH",
  "severity": "CRITICAL",
  "sensor": "ch4",
  "value": 1.45,
  "threshold": 1.25,
  "grid_cell": [3, 5],
  "message": "CH4 level exceeded safe threshold of 1.25% at cell [3,5]"
}
```

### 3. Worker Detected & Rescue Path Schema (`worker_found`)
```json
{
  "worker_id": "VICTIM_01",
  "confidence": 0.94,
  "grid_position": [8, 7],
  "thermal_max_temp": 37.4,
  "rescue_path": [
    [1, 1], [1, 2], [2, 2], [3, 2], [4, 2], 
    [5, 3], [6, 4], [7, 5], [8, 6], [8, 7]
  ],
  "path_distance_m": 14.2
}
```

---

## 🧠 Dynamic A* Pathfinding Engine

The pathfinder operates over a 2D occupancy grid where cells are classified into three states:
* `0 = CLEAR`: Navigable tunnel cell.
* `1 = STRUCTURAL_OBSTACLE`: Blocked by cave-in or rubble.
* `2 = GAS_HAZARD`: High concentration gas pocket ($\text{CH}_4 \ge 1.25\%$ or $\text{CO} \ge 25\text{ ppm}$).

### Node Evaluation Function
$$f(n) = g(n) + h(n) + w(n)$$

Where:
* $g(n)$: Exact movement cost from start node to node $n$.
* $h(n)$: Euclidean distance heuristic to worker destination:
  $$h(n) = \sqrt{(x_{worker} - x_n)^2 + (y_{worker} - y_n)^2}$$
* $w(n)$: Hazard Penalty Weight factor. If node $n$ is adjacent to a gas pocket, $w(n) = +50$ cost multiplier to ensure a safe buffer zone.

```mermaid
graph LR
    Start["Rover Start Position [1,1]"] --> Search["Evaluate Neighboring Grid Cells"]
    Search --> CostCalc["Calculate Cost f(n) = g(n) + h(n) + HazardPenalty"]
    CostCalc --> CheckHazard{"Is Cell Red Gas Pocket?"}
    CheckHazard -->|Yes| Reject["Assign Infinite Cost / Avoid"]
    CheckHazard -->|No| Accept["Add to Open Evaluation Set"]
    Accept --> Destination{"Reached Worker Coord?"}
    Destination -->|No| Search
    Destination -->|Yes| Trace["Reconstruct Safe Rescue Path"]
    Trace --> Render["Draw Green Route on Mission Control Grid"]
```

---

## 🕹️ Mission Control UI & Visual System State

```mermaid
stateDiagram-v2
    [*] --> Idle_Patrol: System Power On & Connect
    
    state Idle_Patrol {
        [*] --> Scanning: Rover Exploring Tunnels
        Scanning --> Normal_Telemetry: Gauges Green
    }

    Idle_Patrol --> Hazard_Alert: Telemetry > Threshold
    state Hazard_Alert {
        [*] --> Red_Screen_Flash: Screen Flashes Red
        Red_Screen_Flash --> Log_Hazard_Cell: Mark Red Box on Grid
    }

    Idle_Patrol --> Worker_Found: Thermal AI Detects Heat (37°C)
    state Worker_Found {
        [*] --> Pin_Worker: Draw Worker Icon on Grid
        Pin_Worker --> Run_A_Star: Execute A* Pathfinding
        Run_A_Star --> Draw_Safe_Vector: Render Green Path Line
    }

    Hazard_Alert --> Evacuate_Commander: Gas Level Critical
    Worker_Found --> Rescue_Dispatched: Commander Approves Path
```

---

## 📋 Evaluation & Demonstration Scenarios

1. **Scenario 1 — Gas Leak Breach (`Demo Key 1`):**
   * Artificially spikes $\text{CH}_4$ to $1.45\%$ and $\text{CO}$ to $28\text{ PPM}$.
   * **Result:** Gauges switch to Red zone, red flash alert overlays screen, and gas cells $[2,5]$ & $[3,5]$ highlight as danger zones.

2. **Scenario 2 — Structural Cave-In (`Demo Key 2`):**
   * Simulates sudden obstacle detection via LiDAR.
   * **Result:** Grid cells marked blocked, dynamic path recalculation re-routes around rubble.

3. **Scenario 3 — Worker Rescue Lock (`Demo Key 3`):**
   * Simulates thermal AI lock on trapped worker heat signature at $[8,7]$.
   * **Result:** Worker pin drops on grid, $A^*$ pathfinder computes optimal path avoiding gas pockets, green vector drawn for rescue team.

---

## 🚀 Key Differentiators & Hackathon Edge

1. **Zero Human Entry Risk:** Surface command receives a complete tactical map before any human steps inside.
2. **Dust-Penetrating Thermal Vision:** Standard cameras fail in coal dust; FLIR radiometric thermal imaging locates survivors by heat signatures.
3. **Gas-Aware Path Generation:** Does not merely find the shortest path—actively routes around volatile gas pockets.
4. **100% Offline Capability:** Runs completely locally on a surface laptop without internet or cloud dependency.

---
> *"Raw data goes in underground. Clear, life-saving decisions come out on screen."*  
> **We don't guess. We know.**
