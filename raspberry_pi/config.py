# Raspberry Pi Configuration
RPI_IP = "192.168.4.241"

# Ports
ESP32_PORT     = 5005
COMMAND_PORT   = 5006
TELEMETRY_PORT = 5007

# ──────────────────────────────────────────────────────────
# L298N Motor Driver — CORRECTED FOR YOUR PHYSICAL PINS
# ──────────────────────────────────────────────────────────
IN1 = 25   # Pi pin 22 — Left  Motor Backward
IN2 = 22   # Pi pin 15 — Left  Motor Forward
IN3 = 6    # Pi pin 31 — Right Motor Backward
IN4 = 18   # Pi pin 12 — Right Motor Forward