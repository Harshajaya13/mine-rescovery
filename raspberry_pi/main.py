import socket
import json
import threading
import time
import config
from motor_controller import MotorController
from navigation import Navigator

# Initialize Hardware
motors = MotorController()
nav = Navigator(motors)

# Global State
sensor_data_cache = {}
last_signal_time = time.time()
signal_lost = False

# Connected laptop telemetry clients (laptop connects to us on port 5007)
telemetry_clients = []
telemetry_clients_lock = threading.Lock()


# ─────────────────────────────────────────
# 1. HANDLE ESP32 SENSOR DATA (port 5005)
# ─────────────────────────────────────────
def handle_esp32_sensor_data():
    """Listens for ESP32 connection on port 5005. Forwards data to all laptop clients."""
    global sensor_data_cache, last_signal_time

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', config.ESP32_PORT))
    srv.listen(1)
    print(f"[ESP32] Listening on port {config.ESP32_PORT} ...")

    while True:
        conn, addr = srv.accept()
        print(f"[ESP32] Connected from {addr}")
        last_signal_time = time.time()

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                lines = data.decode(errors='ignore').strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                        sensor_data_cache = payload
                        last_signal_time = time.time()

                        # Broadcast to all connected laptop clients
                        broadcast_to_laptop(payload)

                        # Local emergency safety check (acts immediately, no laptop needed)
                        check_safety(payload)

                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                print(f"[ESP32] Error: {e}")
                break

        print("[ESP32] Disconnected.")
        conn.close()


# ─────────────────────────────────────────
# 2. TELEMETRY SERVER (port 5007)
#    Laptop connects here to receive live data stream
# ─────────────────────────────────────────
def handle_telemetry_subscription():
    """Laptop connects to this port to subscribe to the sensor data stream."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', config.TELEMETRY_PORT))
    srv.listen(5)
    print(f"[Telemetry] Listening on port {config.TELEMETRY_PORT} for laptop ...")

    while True:
        conn, addr = srv.accept()
        print(f"[Telemetry] Laptop subscribed from {addr}")
        with telemetry_clients_lock:
            telemetry_clients.append(conn)


def start_telemetry_heartbeat():
    """Periodically broadcasts cached telemetry to keep laptop connected and updated."""
    while True:
        time.sleep(1.0)
        # Default payload if ESP32 hasn't sent data yet
        payload = {
            "source": sensor_data_cache.get("source", "rpi_idle"),
            "distance_cm": sensor_data_cache.get("distance_cm", "--"),
            "gas_detected": sensor_data_cache.get("gas_detected", 0),
            "rssi": sensor_data_cache.get("rssi", "--")
        }
        broadcast_to_laptop(payload)


def broadcast_to_laptop(payload):
    """Send sensor data to all connected laptop clients."""
    msg = (json.dumps(payload) + '\n').encode()
    dead = []
    with telemetry_clients_lock:
        for client in telemetry_clients:
            try:
                client.sendall(msg)
            except:
                dead.append(client)
        for d in dead:
            try:
                d.close()
            except:
                pass
            telemetry_clients.remove(d)


# ─────────────────────────────────────────
# 3. COMMAND SERVER (port 5006)
#    Laptop connects here to send motor commands
# ─────────────────────────────────────────
def listen_for_laptop_commands():
    """Accepts motor/navigation commands sent from the laptop AI server."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', config.COMMAND_PORT))
    srv.listen(5)
    print(f"[Commands] Listening on port {config.COMMAND_PORT} for laptop commands ...")

    while True:
        conn, addr = srv.accept()
        try:
            data = conn.recv(1024)
            if data:
                command = json.loads(data.decode())
                action = command.get('action')
                if action:
                    print(f"[Commands] Received: {action}")
                    nav.execute_command(action, duration=0.5)
        except Exception as e:
            print(f"[Commands] Error: {e}")
        finally:
            conn.close()


# ─────────────────────────────────────────
# 4. LOCAL SAFETY CHECK
# ─────────────────────────────────────────
def check_safety(payload):
    """Immediate local response to hazards — does not wait for laptop AI."""
    if payload.get('gas_detected') == 1:
        print("⚠ CRITICAL: Gas Detected! Stopping motors.")
        motors.stop()

    if 0 < payload.get('distance_cm', 100) < 15:
        print("⚠ WARNING: Obstacle very close! Stopping.")
        motors.stop()


# ─────────────────────────────────────────
# 5. SIGNAL MONITOR
# ─────────────────────────────────────────
def monitor_signal_strength():
    """If no data from ESP32 for 5 seconds, trigger auto-return."""
    global signal_lost, last_signal_time
    while True:
        elapsed = time.time() - last_signal_time
        if elapsed > 5.0 and not signal_lost:
            signal_lost = True
            print("[Monitor] ESP32 signal lost! Triggering auto-return.")
            nav.auto_return_to_signal()
        elif elapsed <= 5.0 and signal_lost:
            signal_lost = False
            print("[Monitor] Signal recovered.")
        time.sleep(1)


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("=" * 40)
    print("  Mine Rescue Rover — RPi Client")
    print(f"  RPi IP: {config.RPI_IP}")
    print("=" * 40)

    try:
        threading.Thread(target=handle_esp32_sensor_data,      daemon=True).start()
        threading.Thread(target=handle_telemetry_subscription,  daemon=True).start()
        threading.Thread(target=start_telemetry_heartbeat,       daemon=True).start()
        threading.Thread(target=monitor_signal_strength,        daemon=True).start()

        # Main thread handles laptop commands (blocking accept loop)
        listen_for_laptop_commands()

    except KeyboardInterrupt:
        print("\n[Main] Shutting down...")
    finally:
        motors.cleanup()


if __name__ == "__main__":
    main()
