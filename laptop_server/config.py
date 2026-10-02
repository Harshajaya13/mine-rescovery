# Laptop Server Configuration

# ── Network ──────────────────────────────────────
HOST    = '0.0.0.0'
WEB_PORT = 5000

# ESP32 Rover (Replaces Raspberry Pi)
RPI_IP           = "192.168.4.XXX"   # <-- CHANGE THIS TO YOUR ESP32 IP ADDRESS
RPI_COMMAND_PORT = 5006   # Laptop → ESP32: send motor commands
RPI_TELEMETRY_PORT = 5007 # Laptop → ESP32: subscribe to sensor stream

# ── Hardware ─────────────────────────────────────
# ESP-CAM stream URL (get IP from ESP-CAM serial monitor after flashing)
CAMERA_URL = "http://192.168.4.209:81/stream"

# ── AI/ML ────────────────────────────────────────
YOLO_MODEL_PATH      = "yolov8n.pt"   # Auto-downloads on first run (~6MB)
CONFIDENCE_THRESHOLD = 0.5

# ── Map ──────────────────────────────────────────
GRID_SIZE = 10  # 10x10 mine section grid
