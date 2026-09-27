import RPi.GPIO as GPIO
import time
import config


class MotorController:
    """
    Motor controller for L298N using direction pins only.
    Right side: IN1 (Fwd), IN2 (Bwd)
    Left  side: IN3 (Fwd), IN4 (Bwd)
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
        # Right: forward (IN1=1), Left: forward (IN3=1)
        self._set(1, 0, 1, 0)
        print("[Motors] Forward")

    def move_backward(self):
        # Right: backward (IN2=1), Left: backward (IN4=1)
        self._set(0, 1, 0, 1)
        print("[Motors] Backward")

    def turn_left(self):
        # Right: forward (IN1=1), Left: backward (IN4=1)
        self._set(1, 0, 0, 1)
        print("[Motors] Turn Left")

    def turn_right(self):
        # Right: backward (IN2=1), Left: forward (IN3=1)
        self._set(0, 1, 1, 0)
        print("[Motors] Turn Right")

    def stop(self):
        self._set(0, 0, 0, 0)
        print("[Motors] Stop")

    def cleanup(self):
        self.stop()
        GPIO.cleanup()
        print("[Motors] GPIO cleaned up")
