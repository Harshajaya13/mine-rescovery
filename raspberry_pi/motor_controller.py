import RPi.GPIO as GPIO
import time
import config


class MotorController:
    """
    Motor controller for L298N — Direction pins only (full speed, no PWM).

    YOUR WIRING (Physical Pins & Observed Behavior):
    ┌─────────────────────────────────────────────┐
    │  IN1 (Pin 11, BCM 17) → LEFT  Motor Backward│
    │  IN2 (Pin 13, BCM 27) → LEFT  Motor Forward │
    │  IN3 (Pin 15, BCM 22) → RIGHT Motor Backward│
    │  IN4 (Pin 18, BCM 24) → RIGHT Motor Forward │
    └─────────────────────────────────────────────┘

    DIRECTION LOGIC:
    Forward    → IN2=HIGH, IN4=HIGH
    Backward   → IN1=HIGH, IN3=HIGH
    Turn Left  → LEFT Bwd (IN1=HIGH) + RIGHT Fwd (IN4=HIGH)
    Turn Right → LEFT Fwd (IN2=HIGH) + RIGHT Bwd (IN3=HIGH)
    """

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.pins = [config.IN1, config.IN2, config.IN3, config.IN4]

        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        print("[Motors] GPIO ready. Pins:", self.pins)

    def _set(self, in1, in2, in3, in4):
        GPIO.output(config.IN1, GPIO.HIGH if in1 else GPIO.LOW)
        GPIO.output(config.IN2, GPIO.HIGH if in2 else GPIO.LOW)
        GPIO.output(config.IN3, GPIO.HIGH if in3 else GPIO.LOW)
        GPIO.output(config.IN4, GPIO.HIGH if in4 else GPIO.LOW)

    def move_forward(self):
        # Left Fwd (IN2=HIGH) + Right Fwd (IN4=HIGH)
        self._set(0, 1, 0, 1)
        print("[Motors] Forward")

    def move_backward(self):
        # Left Bwd (IN1=HIGH) + Right Bwd (IN3=HIGH)
        self._set(1, 0, 1, 0)
        print("[Motors] Backward")

    def turn_left(self):
        # Left Bwd (IN1=HIGH) + Right Fwd (IN4=HIGH)
        self._set(1, 0, 0, 1)
        print("[Motors] Turn Left")

    def turn_right(self):
        # Left Fwd (IN2=HIGH) + Right Bwd (IN3=HIGH)
        self._set(0, 1, 1, 0)
        print("[Motors] Turn Right")

    def stop(self):
        self._set(0, 0, 0, 0)
        print("[Motors] Stop")

    def cleanup(self):
        self.stop()
        GPIO.cleanup()
        print("[Motors] GPIO cleaned up")