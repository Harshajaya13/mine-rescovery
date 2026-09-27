# Raspberry Pi Configuration
RPI_IP = "10.59.164.241"

# Ports RPi listens on
ESP32_PORT     = 5005   # ESP32 connects here to send sensor data
COMMAND_PORT   = 5006   # Laptop connects here to send motor commands
TELEMETRY_PORT = 5007   # Laptop connects here to receive live sensor stream

# ──────────────────────────────────────────────────────────
# L298N Motor Driver — Direction pins (Rover Perspective)
# Physical Pins: 11, 13, 15, 18 (BCM 17, 22, 24, 27)
# ──────────────────────────────────────────────────────────
IN1 = 17   # Physical Pin 11  — Right Forward
IN2 = 22   # Physical Pin 13  — Right Backward
IN3 = 24   # Physical Pin 15  — Left  Forward
IN4 = 27   # Physical Pin 18  — Left  Backward