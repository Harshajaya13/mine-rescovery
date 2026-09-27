import RPi.GPIO as GPIO
import time
import config  # Uses pin definitions from config.py

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins = {
    "IN1 - Right Forward (Physical Pin 11)": config.IN1,  # BCM 17
    "IN2 - Right Reverse (Physical Pin 13)": config.IN2,  # BCM 22
    "IN3 - Left Forward  (Physical Pin 15)": config.IN3,  # BCM 24
    "IN4 - Left Reverse  (Physical Pin 18)": config.IN4   # BCM 27
}

# Setup all pins to OUTPUT and LOW initially
for name, pin in pins.items():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

try:
    print("Starting motor test...\n")
    for name, pin in pins.items():
        print(f"Testing {name} [BCM {pin}] for 5 seconds...")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(pin, GPIO.LOW)
        print(f"DONE testing {name}.\n")

except KeyboardInterrupt:
    print("\n[Test] Interrupted by user!")
finally:
    for name, pin in pins.items():
        try:
            GPIO.output(pin, GPIO.LOW)
        except Exception:
            pass
    GPIO.cleanup()
    print("All motor pins shut down & GPIO cleaned up!")

