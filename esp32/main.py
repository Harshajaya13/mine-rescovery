import machine
import time
import network
import socket
import json

# --- CONFIGURATION ---
SSID = "kesava"              # WiFi network name
PASSWORD = "123456789"  # ← fill your WiFi password here
SERVER_IP = "192.168.4.241"  # Raspberry Pi IP
SERVER_PORT = 5005

# --- HARDWARE SETUP ---
# Ultrasonic Sensor
TRIG_PIN = 33
ECHO_PIN = 32
trig = machine.Pin(TRIG_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)

# MQ-6 Gas Sensor
MQ6_DO_PIN = 27
mq6_do = machine.Pin(MQ6_DO_PIN, machine.Pin.IN)

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
    print('\nNetwork config:', wlan.ifconfig())
    return wlan
    

# --- SENSOR READING ---
TIMEOUT_US = 30000  # 30ms timeout (~5m max range)

def get_distance():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    try:
        # time_pulse_us(pin, pulse_level, timeout_us)
        pulse_duration = machine.time_pulse_us(echo, 1, 30000)
        if pulse_duration < 0:
            return 999.0
        distance = (pulse_duration * 0.0343) / 2
        return round(distance, 2)
    except OSError:
        return 999.0

def get_gas_status():
    # DO pin goes LOW (0) when gas is detected, HIGH (1) normally
    return 1 if mq6_do.value() == 0 else 0

# --- MAIN LOOP ---
def main():
    wlan = connect_wifi()
    
    # Setup socket to send data to laptop
    s = socket.socket()
    while True:
        try:
            print(f"Connecting to server {SERVER_IP}:{SERVER_PORT}")
            s.connect((SERVER_IP, SERVER_PORT))
            print("Connected!")
            break
        except Exception as e:
            print("Connection failed, retrying in 5s...", e)
            time.sleep(5)

    while True:
        try:
            dist = get_distance()
            gas = get_gas_status()
            rssi = wlan.status('rssi')
            
            data = {
                "source": "esp32_sensors",
                "distance_cm": round(dist, 2),
                "gas_detected": gas,
                "rssi": rssi
            }
            
            payload = json.dumps(data) + '\n'
            s.send(payload.encode())
            print(f"Sent: {payload.strip()}")
            
        except OSError as e:
            print("Error sending data:", e)
            # Try to reconnect
            time.sleep(3)
            try:
                s.close()
            except:
                pass
            s = socket.socket()
            while True:
                try:
                    print("Reconnecting to server...")
                    s.connect((SERVER_IP, SERVER_PORT))
                    print("Reconnected!")
                    break
                except:
                    time.sleep(5)
                
        time.sleep(0.5)  # Send data every 500ms

# MicroPython: directly call main (no __name__ == '__main__' support)
main()
