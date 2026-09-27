from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO
import cv2
import threading
import json
import socket
import time
import config
from yolo_detector import ObjectDetector
from mine_mapper import MineMapper
from ai_analysis import AIAnalyzer

app = Flask(__name__, template_folder='dashboard/templates', static_folder='dashboard/static')
socketio = SocketIO(app, cors_allowed_origins="*")

# Globals
detector = ObjectDetector()
mapper   = MineMapper()
ai       = AIAnalyzer(mapper)
latest_telemetry = {}
ai_report        = {}
auto_mode        = False



# ─────────────────────────────────────────
# SEND COMMAND TO RPI  (Laptop → RPi:5006)
# ─────────────────────────────────────────
def send_command_to_rpi(action):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((config.RPI_IP, config.RPI_COMMAND_PORT))
        s.sendall(json.dumps({"action": action}).encode())
        s.close()
        print(f"[Command → RPi] {action}")

        # Mirror on virtual map
        if action == 'forward':   mapper.move_forward()
        elif action == 'left':    mapper.turn_left()
        elif action == 'right':   mapper.turn_right()

    except Exception as e:
        print(f"[Command] Failed to send '{action}' to RPi: {e}")


# ─────────────────────────────────────────
# SUBSCRIBE TO RPi TELEMETRY (Laptop → RPi:5007)
# RPi streams sensor data to us continuously
# ─────────────────────────────────────────
def subscribe_to_rpi_telemetry():
    global latest_telemetry, ai_report
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((config.RPI_IP, config.RPI_TELEMETRY_PORT))
            print(f"[Telemetry] Connected to RPi at {config.RPI_IP}:{config.RPI_TELEMETRY_PORT}")

            buffer = ""
            while True:
                chunk = s.recv(1024).decode(errors='ignore')
                if not chunk:
                    break
                buffer += chunk

                # Process all complete newline-terminated JSON lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                        latest_telemetry = payload

                        # AI analysis
                        ai_report = ai.analyze_situation(
                            latest_telemetry,
                            detector.get_latest_detections()
                        )

                        # Push to dashboard via SocketIO
                        socketio.emit('telemetry_update', {
                            'sensor':    latest_telemetry,
                            'ai_report': ai_report,
                            'map':       mapper.get_map_state(),
                            'auto_mode': auto_mode
                        })

                        # Autonomous AI actions (only if Auto Mode is ON)
                        if auto_mode:
                            action = ai_report.get('suggested_action', '')
                            if action == 'reroute':
                                send_command_to_rpi('right')
                            elif action == 'evacuate':
                                send_command_to_rpi('stop')

                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            print(f"[Telemetry] Lost connection to RPi: {e}. Retrying in 5s...")
            time.sleep(5)


# ─────────────────────────────────────────
# VIDEO FEED WITH YOLO (ESP-CAM stream)
# ─────────────────────────────────────────
def generate_frames():
    def open_capture():
        c = cv2.VideoCapture(config.CAMERA_URL)
        if not c.isOpened():
            print(f"[Video] Failed to open {config.CAMERA_URL}. Falling back to webcam 0.")
            c = cv2.VideoCapture(0)
        return c

    cap = open_capture()
    while True:
        success, frame = cap.read()
        if not success:
            print("[Video] Stream lost. Reconnecting in 3s...")
            cap.release()
            time.sleep(3)
            cap = open_capture()
            continue

        # Flip the video 180 degrees (upside down mount)
        frame = cv2.flip(frame, -1)

        annotated_frame, _ = detector.process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


# ─────────────────────────────────────────
# FLASK ROUTES
# ─────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/command', methods=['POST'])
def handle_command():
    data   = request.json
    action = data.get('action')
    if action:
        send_command_to_rpi(action)
    return jsonify({"status": "ok"})

@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    global auto_mode
    auto_mode = not auto_mode
    print(f"[System] Auto Mode is now {'ON' if auto_mode else 'OFF'}")
    return jsonify({"auto_mode": auto_mode})


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 45)
    print("  Mine Rescue Rover — Laptop AI Server")
    print(f"  Connecting to RPi at {config.RPI_IP}")
    print(f"  Dashboard: http://localhost:{config.WEB_PORT}")
    print("=" * 45)

    # Subscribe to RPi telemetry stream in background
    threading.Thread(target=subscribe_to_rpi_telemetry, daemon=True).start()

    # Start Flask + SocketIO
    socketio.run(app, host=config.HOST, port=config.WEB_PORT,
                 debug=False, use_reloader=False)
