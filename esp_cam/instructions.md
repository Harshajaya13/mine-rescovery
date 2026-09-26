# ESP-CAM Setup Instructions

For the ESP32-CAM, the easiest and most robust way to get a video stream for YOLO to process is to use the standard `CameraWebServer` example provided in the Arduino IDE.

## Steps:
1. Open the **Arduino IDE**.
2. Go to **File -> Examples -> ESP32 -> Camera -> CameraWebServer**.
3. In the code, select your camera model by uncommenting it (usually `#define CAMERA_MODEL_AI_THINKER`).
4. Enter your WiFi SSID and Password in the `ssid` and `password` variables.
5. Upload the code to your ESP32-CAM using an FTDI programmer (since ESP-CAM usually lacks a built-in USB port).
6. Open the **Serial Monitor** at 115200 baud, press the reset button on the ESP32-CAM.
7. Note the IP address printed in the Serial Monitor (e.g., `http://192.168.1.15`).
8. Update `laptop_server/config.py` with this IP address (`CAMERA_URL = "http://192.168.1.15:81/stream"`).
