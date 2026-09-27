import RPi.GPIO as GPIO
import time
import config  # Uses pin definitions from config.py

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins = {
    "IN1 - Left  Motor Backward (Pin 11, BCM 17)": config.IN1,
    "IN2 - Left  Motor Forward  (Pin 13, BCM 27)": config.IN2,
    "IN3 - Right Motor Backward (Pin 15, BCM 22)": config.IN3,
    "IN4 - Right Motor Forward  (Pin 18, BCM 24)": config.IN4,
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

