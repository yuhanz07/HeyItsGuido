################################################################
# PS5 Controller Class for ND Robotics Course
# 3-7-2025
# Professor McLaughlin
################################################################
import pygame
import time

class PS5_Controller:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self.firstMessage = True
        self.last_press_time = {}
        self.debounce_time = 0.5

        # Initialize last echo times for joysticks
        self.lastEchoLeftTime = 0
        self.lastEchoRightTime = 0

        # Joystick Control Variables
        self.control_request = {
            "joystickLeftSending": False,
            "joystickRightSending": False,
            "reqMade": False,
            "reqLeftJoyMade": False,
            "reqRightJoyMade": False,
            "reqLeftJoyUp": False,
            "reqLeftJoyDown": False,
            "reqLeftJoyLeft": False,
            "reqLeftJoyRight": False,
            "reqLeftJoyYValue": 0,
            "reqLeftJoyXValue": 0,
            "reqRightJoyUp": False,
            "reqRightJoyDown": False,
            "reqRightJoyLeft": False,
            "reqRightJoyRight": False,
            "reqRightJoyYValue": 0,
            "reqRightJoyXValue": 0,
            "reqArrowUp": False,
            "reqArrowDown": False,
            "reqArrowLeft": False,
            "reqArrowRight": False,
            "reqCircle": False,
            "reqCross": False,
            "reqTriangle": False,
            "reqSquare": False,
            "reqL1": False,
            "reqL2": False,
            "reqR1": False,
            "reqR2": False,
            "reqShare": False,
            "reqOptions": False,
            "reqPS": False,
            "reqJSLeftButton": False,
            "reqJSRightButton": False
        }

    def initialize_controller(self):
        # Waits for a joystick to connect
        while pygame.joystick.get_count() == 0:
            if self.firstMessage:
                print("Waiting for a joystick to connect...")
                self.firstMessage = False
            event = pygame.event.wait()
            if event.type == pygame.JOYDEVICEADDED:
                pygame.joystick.init()
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print(f"Detected joystick: {self.joystick.get_name()}")

    def is_debounced(self, key):
        # Debounces controller inputs
        current_time = time.time()
        if key not in self.last_press_time or (current_time - self.last_press_time[key] > self.debounce_time):
            self.last_press_time[key] = current_time
            return True
        return False

    def check_controls(self):
        # Checks button and joystick states
        # Check buttons
        button_map = {
            0: "reqCross", 1: "reqCircle", 2: "reqTriangle", 3: "reqSquare",
            4: "reqL1", 5: "reqR1", 6: "reqL2", 7: "reqR2",
            8: "reqShare", 9: "reqOptions", 10: "reqPS",
            11: "reqJSLeftButton", 12: "reqJSRightButton"
        }

        for button, request_key in button_map.items():
            if self.joystick.get_button(button) and self.is_debounced(button):
                print(f"Button {request_key} pressed.")
                self.control_request[request_key] = True
                self.control_request["reqMade"] = True

        # Check D-pad (hat switch)
        hat = self.joystick.get_hat(0)
        if hat == (0, 1) and self.is_debounced(13):
            print("Button Arrow_Up pressed.")
            self.control_request["reqArrowUp"] = True
            self.control_request["reqMade"] = True

        if hat == (0, -1) and self.is_debounced(14):
            print("Button Arrow_Down pressed.")
            self.control_request["reqArrowDown"] = True
            self.control_request["reqMade"] = True

        if hat == (-1, 0) and self.is_debounced(15):
            print("Button Arrow_Left pressed.")
            self.control_request["reqArrowLeft"] = True
            self.control_request["reqMade"] = True

        if hat == (1, 0) and self.is_debounced(16):
            print("Button Arrow_Right pressed.")
            self.control_request["reqArrowRight"] = True
            self.control_request["reqMade"] = True

        # Check left joystick
        self.process_joystick(0, 1, "Left")

        # Check right joystick
        self.process_joystick(3, 4, "Right")

    def process_joystick(self, axis_x, axis_y, side):
        # Handles joystick movements and manages flow control with a 50ms print rate limit
        current_time = time.time()
        control_prefix = f"req{side}Joy"
        sending_flag = f"joystick{side}Sending"
        last_echo_time = f"lastEcho{side}Time"
 
        lx = self.joystick.get_axis(axis_x)
        ly = self.joystick.get_axis(axis_y)
        moving = abs(lx) > 0.1 or abs(ly) > 0.1

        if moving:
            if not self.control_request[sending_flag]:
                print(f"Joystick {side} started sending.")
            self.control_request[sending_flag] = True
            self.control_request[f"{control_prefix}Made"] = True

            # Set movement directions
            self.control_request[f"{control_prefix}Up"] = ly < -0.1
            self.control_request[f"{control_prefix}Down"] = ly > 0.1
            self.control_request[f"{control_prefix}Right"] = lx > 0.1
            self.control_request[f"{control_prefix}Left"] = lx < -0.1

            # Convert joystick range (-1.0 to 1.0) to Sabertooth motor controller range (-127 to 127)
            lx_int = self.map_integer(lx, -1, 1, -127, 127)
            ly_int = self.map_integer(ly, -1, 1, -127, 127)

            self.control_request[f"{control_prefix}YValue"] = ly_int
            self.control_request[f"{control_prefix}XValue"] = lx_int

            # Only print joystick data if at least 50ms has passed
            if current_time - getattr(self, last_echo_time) >= 0.05:
                print(f"Joystick {side} data sent: Y: {self.control_request[f'{control_prefix}YValue']} X: {self.control_request[f'{control_prefix}XValue']}")
                setattr(self, last_echo_time, current_time)

        elif self.control_request[sending_flag]:
            print(f"Joystick {side} Stopped")
            self.control_request[sending_flag] = False
            self.control_request[f"{control_prefix}Made"] = False
            self.control_request[f"{control_prefix}Up"] = False
            self.control_request[f"{control_prefix}Down"] = False
            self.control_request[f"{control_prefix}Left"] = False
            self.control_request[f"{control_prefix}Right"] = False
            self.control_request[f"{control_prefix}YValue"] = 0
            self.control_request[f"{control_prefix}XValue"] = 0

    def map_integer(self, value, old_min, old_max, new_min, new_max):
        # Maps a value from one range to another while preserving negative values
        if old_max - old_min == 0:
            raise ValueError("Old range cannot be zero")
        return round(new_min + (value - old_min) * (new_max - new_min) / (old_max - old_min))

    def reset_controller_state(self):
        # Resets only button and arrow request variables after each loop
        keys_to_reset = [
            "reqMade", "reqArrowUp", "reqArrowDown", "reqArrowLeft", "reqArrowRight",
            "reqCircle", "reqCross", "reqTriangle", "reqSquare",
            "reqL1", "reqL2", "reqR1", "reqR2",
            "reqShare", "reqOptions", "reqPS",
            "reqJSLeftButton", "reqJSRightButton"
        ]

        for key in keys_to_reset:
            self.control_request[key] = False
