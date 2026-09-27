# Raspberry Pi Configuration
RPI_IP = "10.59.164.241"

# Ports
ESP32_PORT     = 5005
COMMAND_PORT   = 5006
TELEMETRY_PORT = 5007

# ──────────────────────────────────────────────────────────
# L298N Motor Driver — CORRECTED FOR YOUR PHYSICAL PINS
# ──────────────────────────────────────────────────────────
IN1 = 17   # Physical Pin 11 — Left  Motor Backward
IN2 = 27   # Physical Pin 13 — Left  Motor Forward
IN3 = 22   # Physical Pin 15 — Right Motor Backward
IN4 = 24   # Physical Pin 18 — Right Motor Forward