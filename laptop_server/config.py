# Laptop Server Configuration

# ── Network ──────────────────────────────────────
HOST    = '0.0.0.0'
WEB_PORT = 5000

# Raspberry Pi (fixed IP — everything connects to RPi)
RPI_IP           = "10.59.164.241"
RPI_COMMAND_PORT = 5006   # Laptop → RPi: send motor commands
RPI_TELEMETRY_PORT = 5007 # Laptop → RPi: subscribe to sensor stream

# ── Hardware ─────────────────────────────────────
# ESP-CAM stream URL (get IP from ESP-CAM serial monitor after flashing)
CAMERA_URL = "http://10.59.164.209:81/stream"

# ── AI/ML ────────────────────────────────────────
YOLO_MODEL_PATH      = "yolov8n.pt"   # Auto-downloads on first run (~6MB)
CONFIDENCE_THRESHOLD = 0.5

# ── Map ──────────────────────────────────────────
GRID_SIZE = 10  # 10x10 mine section grid
