import machine
import time
import network
import socket
import json
import _thread

# --- CONFIGURATION ---
SSID = "kesava"
PASSWORD = "123456789"
COMMAND_PORT = 5006
TELEMETRY_PORT = 5007

# --- HARDWARE SETUP ---
# Ultrasonic Sensor
TRIG_PIN = 33
ECHO_PIN = 32
trig = machine.Pin(TRIG_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)

# MQ-6 Gas Sensor
MQ6_DO_PIN = 27
mq6_do = machine.Pin(MQ6_DO_PIN, machine.Pin.IN)

# Motor Driver L298N (New Wiring!)
IN1 = machine.Pin(26, machine.Pin.OUT)  # Left Backward
IN2 = machine.Pin(14, machine.Pin.OUT)  # Left Forward
IN3 = machine.Pin(12, machine.Pin.OUT)  # Right Backward
IN4 = machine.Pin(13, machine.Pin.OUT)  # Right Forward

def stop_motors():
    IN1.value(0); IN2.value(0); IN3.value(0); IN4.value(0)

stop_motors()

# --- WIFI CONNECTION ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
            print('.', end='')
    ip = wlan.ifconfig()[0]
    print('\nNetwork config:', wlan.ifconfig())
    print('ESP32 IP:', ip)
    return wlan, ip

# --- SENSOR LOGIC ---
def get_distance():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    try:
        pulse_duration = machine.time_pulse_us(echo, 1, 30000)
        if pulse_duration < 0: return 999.0
        return round((pulse_duration * 0.0343) / 2, 2)
    except OSError:
        return 999.0

def get_gas_status():
    return 1 if mq6_do.value() == 0 else 0

# --- TELEMETRY SERVER (Port 5007) ---
def telemetry_server_task():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', TELEMETRY_PORT))
    srv.listen(1)
    print(f"Telemetry listening on port {TELEMETRY_PORT}")
    
    while True:
        try:
            conn, addr = srv.accept()
            print("Telemetry client connected:", addr)
            while True:
                dist = get_distance()
                gas = get_gas_status()
                data = {
                    "source": "esp32_rover",
                    "distance_cm": dist,
                    "gas_detected": gas,
                    "rssi": -50 # placeholder if status not available
                }
                payload = json.dumps(data) + '\n'
                conn.sendall(payload.encode())
                time.sleep(0.5)
        except Exception as e:
            print("Telemetry dropped, waiting for reconnect...")
            try:
                conn.close()
            except: pass

# --- COMMAND SERVER (Port 5006) ---
def command_server_task():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', COMMAND_PORT))
    srv.listen(5)
    print(f"Command listening on port {COMMAND_PORT}")
    
    while True:
        try:
            conn, addr = srv.accept()
            data = conn.recv(1024).decode('utf-8').strip()
            if data:
                try:
                    payload = json.loads(data)
                    action = payload.get("action", "")
                    print("Received command:", action)
                    if action == "forward":
                        IN1.value(0); IN2.value(1); IN3.value(0); IN4.value(1)
                    elif action == "backward":
                        IN1.value(1); IN2.value(0); IN3.value(1); IN4.value(0)
                    elif action == "left":
                        IN1.value(1); IN2.value(0); IN3.value(0); IN4.value(1)
                    elif action == "right":
                        IN1.value(0); IN2.value(1); IN3.value(1); IN4.value(0)
                    elif action == "stop":
                        stop_motors()
                    
                    # Run for 0.5s then stop (like the Pi did)
                    if action != "stop":
                        time.sleep(0.5)
                        stop_motors()
                except Exception as e:
                    print("Parse error:", e)
            conn.close()
        except Exception as e:
            print("Command server error:", e)

# --- MAIN ---
wlan, esp_ip = connect_wifi()

# Start background thread for telemetry
_thread.start_new_thread(telemetry_server_task, ())

# Run command server in main thread
command_server_task()
