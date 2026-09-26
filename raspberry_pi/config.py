# Raspberry Pi Configuration
RPI_IP = "10.59.164.241"

# Ports RPi listens on
ESP32_PORT     = 5005   # ESP32 connects here to send sensor data
COMMAND_PORT   = 5006   # Laptop connects here to send motor commands
TELEMETRY_PORT = 5007   # Laptop connects here to receive live sensor stream

# ──────────────────────────────────────────────────────────
# L298N Motor Driver — Direction pins only (BCM numbering)
# ENA and ENB jumpers are ON (full speed always)
# ──────────────────────────────────────────────────────────
IN1 = 17   # Physical Pin 11  — Left  side (Moved from Pin 16)
IN2 = 24   # Physical Pin 18  — Left  side
IN3 = 27   # Physical Pin 13  — Right side
IN4 = 22   # Physical Pin 15  — Right side
