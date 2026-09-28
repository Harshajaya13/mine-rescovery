import time
import threading

class Navigator:
    def __init__(self, motors):
        self.motors = motors
        self.path_history = []  # List of (action, duration)
        self.is_returning = False
        self._lock = threading.Lock()  # Protect path_history from concurrent access
        
    def execute_command(self, action, duration=0.5):
        if self.is_returning:
            return  # Don't accept new commands while auto-returning
            
        if action == "stop":
            self.motors.stop()
            return  # Don't record stop in history
            
        print(f"Navigation: Executing {action}")
        if action == "forward":
            self.motors.move_forward()
        elif action == "backward":
            self.motors.move_backward()
        elif action == "left":
            self.motors.turn_left()
        elif action == "right":
            self.motors.turn_right()
        else:
            return
            
        time.sleep(duration)      # actually run for the duration
        self.motors.stop()        # then stop
            
        # Record non-stop actions for dead reckoning
        with self._lock:
            self.path_history.append((action, duration))
            
    def auto_return_to_signal(self):
        """
        If signal is lost, reverse the path history step-by-step.
        Runs in its own thread so it does not block the monitor thread.
        """
        if self.is_returning:
            return
        
        with self._lock:
            if not self.path_history:
                print("No path history to retrace.")
                return
            # Take a snapshot and clear history before returning
            path_snapshot = list(self.path_history)
            self.path_history.clear()
            
        # Launch the return in a non-blocking thread
        t = threading.Thread(target=self._execute_return, args=(path_snapshot,), daemon=True)
        t.start()
            
    def _execute_return(self, path_snapshot):
        """Internal: blocking execution of return path in its own thread."""
        print("SIGNAL LOST! Initiating Auto-Return Protocol...")
        self.is_returning = True
        self.motors.stop()
        time.sleep(1)
        
        # Reverse the path steps
        for action, duration in reversed(path_snapshot):
            print(f"Auto-Return: Reversing '{action}' for {duration}s")
            if action == "forward":
                self.motors.move_backward()
            elif action == "backward":
                self.motors.move_forward()
            elif action == "left":
                self.motors.turn_right()
            elif action == "right":
                self.motors.turn_left()
                
            time.sleep(duration)
            self.motors.stop()
            time.sleep(0.15)  # Short pause between steps
            
        print("Auto-Return complete. Waiting for signal recovery.")
        self.is_returning = False
