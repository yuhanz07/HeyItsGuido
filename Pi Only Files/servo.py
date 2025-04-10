################################################################
# Servo Controller for ND Robotics Course
# 3-8-2025
# Professor McLaughlin
################################################################import threading
import threading
import queue
import time
import RPi.GPIO as GPIO

class Servo:
    def __init__(self, pin=22, initial_angle=90, time_per_degree=0.004):
        # param pin: GPIO pin used for the servo (default 22)
        # param initial_angle: starting angle (default 90°)
        # param time_per_degree: estimated seconds needed per degree movement.
        self.pin = pin
        self._queue = queue.Queue()
        self._stop_event = threading.Event()
        self._time_per_degree = time_per_degree
        self._current_angle = initial_angle
        self._last_move_end_time = time.time()  # When the previous move is expected to be done

        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 50)
        self.pwm.start(0)

        # Move to initial angle
        self._set_servo(self._current_angle, initial_setup=True)

        self._worker = threading.Thread(target=self._process_queue, daemon=True)
        self._worker.start()

    def _process_queue(self):
        while not self._stop_event.is_set():
            try:
                command = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if command is None:
                break

            self._set_servo(command)
            self._queue.task_done()
            time.sleep(.001)

    def _set_servo(self, angle, initial_setup=False):
        # Command the servo to move to the specified angle and wait until
        # the expected physical movement should be complete.
        # Map angle to duty cycle (approx. 2.5% to 12.5%)
        duty_cycle = 2.5 + (angle / 180.0) * 10
        self.pwm.ChangeDutyCycle(duty_cycle)

        # Calculate the expected movement time from the angle difference.
        if not initial_setup:
            diff = abs(angle - self._current_angle)
            required_time = diff * self._time_per_degree
        else:
            required_time = 0.3  # a short delay for initial setup

        # Calculate remaining time from previous command if any.
        now = time.time()
        remaining = self._last_move_end_time - now
        wait_time = max(required_time, remaining) if remaining > 0 else required_time

        if wait_time > 0:
            time.sleep(wait_time)

        # Stop PWM to reduce jitter.
        self.pwm.ChangeDutyCycle(0)
        # Update the _current_angle and record expected move finish time.
        self._current_angle = angle
        self._last_move_end_time = time.time()  # now + wait_time is already passed

    def move_to(self, angle):
        if not 0 <= angle <= 180:
            raise ValueError("Angle must be between 0 and 180 degrees.")
        self._queue.put(angle)

    def close(self):
        self._stop_event.set()
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break
        self._queue.put(None)
        self._worker.join()
        self.pwm.stop()
        GPIO.cleanup(self.pin)
        print("Servo shutdown complete")

# Test code
if __name__ == "__main__":
    import sys
    GPIO.setmode(GPIO.BCM)
    servo = Servo()
    try:
        # Rapidly send a sequence of commands
        for angle in [0, 180, 0, 180, 90, 0, 90, 45, 0, 45, 90, 135, 180, 0]:
            print(f"Enqueuing move to {angle}°")
            servo.move_to(angle)
            time.sleep(0.05)  # commands arriving rapidly
        time.sleep(5)
    except KeyboardInterrupt:
        print("Test interrupted.")
    finally:
        servo.close()
        sys.exit(0)
