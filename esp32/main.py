import machine
import time
import network
import socket
import json
import select

# --- CONFIGURATION ---
SSID = "kesava"
PASSWORD = "123456789"
COMMAND_PORT = 5006
TELEMETRY_PORT = 5007

# --- HARDWARE SETUP ---
TRIG_PIN = 33
ECHO_PIN = 32
trig = machine.Pin(TRIG_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)

MQ6_DO_PIN = 27
mq6_do = machine.Pin(MQ6_DO_PIN, machine.Pin.IN)

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
    wlan.disconnect()
    time.sleep(1)
    
    print('Connecting to network...')
    wlan.connect(SSID, PASSWORD)
    timeout = 20 # 20 seconds timeout
    while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            print('.', end='')
            timeout -= 1
    
    if not wlan.isconnected():
        print('\nFailed to connect to WiFi.')
        return wlan, None
    else:
        ip = wlan.ifconfig()[0]
        print('\nNetwork config:', wlan.ifconfig())
        print('ESP32 IP:', ip)
        return wlan, ip

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

# --- MAIN ---
wlan, esp_ip = connect_wifi()

# Setup Command Server
cmd_srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cmd_srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
cmd_srv.bind((esp_ip, COMMAND_PORT))
cmd_srv.listen(1)

# Setup Telemetry Server
tel_srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tel_srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tel_srv.bind((esp_ip, TELEMETRY_PORT))
tel_srv.listen(1)

print(f"Command listening on {esp_ip}:{COMMAND_PORT}")
print(f"Telemetry listening on {esp_ip}:{TELEMETRY_PORT}")

poller = select.poll()
poller.register(cmd_srv, select.POLLIN)
poller.register(tel_srv, select.POLLIN)

tel_conn = None
last_telemetry_time = time.ticks_ms()
motor_stop_time = None

while True:
    events = poller.poll(50)  # non-blocking poll with 50ms timeout
    
    for sock_fd, event in events:
        if sock_fd == tel_srv.fileno():
            # New telemetry client
            if tel_conn:
                tel_conn.close()
            tel_conn, addr = tel_srv.accept()
            print("Telemetry connected:", addr)
            
        elif sock_fd == cmd_srv.fileno():
            # New command client
            cmd_conn, addr = cmd_srv.accept()
            try:
                data = cmd_conn.recv(1024).decode('utf-8').strip()
                if data:
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
                        motor_stop_time = None
                    
                    if action != "stop":
                        # schedule stop 500ms later instead of blocking
                        motor_stop_time = time.ticks_add(time.ticks_ms(), 500)
            except Exception as e:
                print("Command error:", e)
            cmd_conn.close()

    # Handle timed motor stop
    if motor_stop_time and time.ticks_diff(time.ticks_ms(), motor_stop_time) >= 0:
        stop_motors()
        motor_stop_time = None

    # Send Telemetry Data if a client is connected
    if tel_conn and time.ticks_diff(time.ticks_ms(), last_telemetry_time) > 500:
        last_telemetry_time = time.ticks_ms()
        try:
            try:
                current_rssi = wlan.status('rssi')
            except:
                current_rssi = -50
                
            data = {
                "source": "esp32_rover",
                "distance_cm": get_distance(),
                "gas_detected": get_gas_status(),
                "rssi": current_rssi
            }
            tel_conn.sendall((json.dumps(data) + '\n').encode())
        except Exception as e:
            print("Telemetry disconnected")
            tel_conn.close()
            tel_conn = None
