import time
import pygame
import threading
from sabertooth import Sabertooth

class routine_move:
    def __init__(self):
        # Initialize Sabertooth motor controller
        self.saber = Sabertooth()

        # Initialize pygame and controller
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            print("Controller initialized.")
        else:
            print("No controller found. Exiting.")
            pygame.quit()
            raise RuntimeError("Controller not found")

    def drive(self, speed, turn, duration):
        start_time = time.time()
        drive_lag = .04
        last_drivet = time.time()
        while time.time() - start_time < duration:
            if(time.time() - last_drivet > drive_lag):
                self.saber.drive(speed, turn)
                last_drivet = time.time()
        self.saber.drive(0, 0)  # Stop after driving

    def move_forward(self, speed, duration):
        """Move forward with specified speed and duration."""
        print("Moving forward")
        self.drive(-speed, 0, duration)

    def move_backward(self, speed, duration):
        """Move backward with specified speed and duration."""
        print("Moving backward")
        self.drive(speed, 0, duration)

    def turn_left(self, speed, duration):
        """Turn left in place."""
        print("Turning left")
        self.drive(-speed, speed, duration)

    def turn_right(self, speed, duration):
        """Turn right in place."""
        print("Turning right")
        self.drive(speed, -speed, duration)

    def stop(self, duration):
        """Stop the car."""
        print("Stopping")
        self.drive(0, 0, duration)

    def close(self):
        """Cleanup resources."""
        pygame.quit()
        print("Controller closed.")

    def button_pressed(self, button_id=0):
        """Check if a specific button is pressed."""
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and event.button == button_id:
                return True
        return False
