import pygame
import time
from sabertooth import Sabertooth
from ps5_controller import PS5_Controller

import os
import time
import random
import subprocess
import threading
import queue
from pydub import AudioSegment
import pygame
from usb_sound_controller import USB_SoundController

from ambient_sound import AmbientSoundRoutine

import spidev            # For SPI communications
import RPi.GPIO as GPIO  # For controlling GPIO pins
import threading         # For managing threads
import time              # For sleep/delay functions
from PIL import Image, ImageDraw, ImageFont  # For image manipulation
import math              # For geometric calculations
from queue import Queue  # For thread-safe queue

from tft_display import TFTDisplay
from tft_display import TFTRoutine

import atexit

atexit.register(GPIO.cleanup)

# Define TFT display pins (GPIO numbers) based on your wiring.
TFT_CS_PIN = 5     # Chip Select (GPIO5)
TFT_RESET_PIN = 6  # Reset (GPIO6)
TFT_DC_PIN = 26    # Data/Command (GPIO26)

# Display specifications for the 1.8" TFT (ST7735R):
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160


def initialize_controller():
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        print(f"Controller '{controller.get_name()}' initialized.")
        return controller
    else:
        print("No PS5 controller detected. Ambient routine control disabled.")
        return None

def process_controller_events(ambient_routine):
    """
    Checks for PS5 controller events.
    In this example, pressing button 0 toggles the ambient routine.
    """
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            # Toggle the ambient routine on button press (assume button 0).
            if event.button == 0:
                if ambient_routine.running:
                    ambient_routine.stop()
                else:
                    ambient_routine.start()


def move_robot(saber, control_request):
    # Sends motor commands to the Sabertooth motor controller.
    speed = control_request["reqLeftJoyYValue"]
    turn = -control_request["reqLeftJoyXValue"] /2
    saber.drive(speed, turn)


# ---------------- Main Routine ---------------- #
if __name__ == "__main__":
    # Initialize the PS5 Controller class
    ps5 = PS5_Controller()
    ps5.initialize_controller()
    
    # Initialize Sabertooth motor controller
    saber = Sabertooth()
    saber.set_ramping(21)  # Fast Ramping 1-10, Slow 11-20, Intermediate 21-80
    isMoving = False
    
    ps5_last_check_time = time.time()
    ps5_loop_interval = 0.02  # 20ms interval
    
    motor_controller_last_check_time = time.time()
    motor_controller_loop_interval = 0.04  # 40ms interval
        
    # Initialize the sound controller.
    sound_ctrl = USB_SoundController(volume=0.7)
    

    # List of at least 5 different background ambient sounds.
    ambient_sounds = [
        "/home/ndrobotics/code/Pi Only Files /sounds/boxbox.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/f1.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/italiananthem.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/SmoothOperator.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/kimisteeringwheel.mp3"
    ]

    # Create the AmbientSoundRoutine instance.
    ambient_routine = AmbientSoundRoutine(sound_ctrl, ambient_sounds)

    # Initialize PS5 controller (if available).
    controller = initialize_controller()

    # Start the ambient routine by default.
    ambient_routine.start()
    
    # Start display
    display = TFTDisplay()
    
    image_list = [
        "/home/ndrobotics/code/Pi Only Files /images/guido_1.bmp",
        "/home/ndrobotics/code/Pi Only Files /images/guido_mog.bmp",
        "/home/ndrobotics/code/Pi Only Files /images/guido_drill.bmp",
        "/home/ndrobotics/code/Pi Only Files /images/guido_italy.bmp",
        ]
    
    display_routine = TFTRoutine(display, image_list)
 
    display_routine.start()
    

    try:
        # Main loop polls for controller events to toggle ambient sounds.
        while True:
            current_time = time.time()

            # Check PS5 controller state
            if current_time - ps5_last_check_time >= ps5_loop_interval:
                pygame.event.pump()
                ps5.check_controls()
                ps5_last_check_time = current_time

            # Example: Use Arrow Up as a function call trigger
            if ps5.control_request["reqArrowUp"]:
                print("This should call by function tied to Arrow Up")

            # Move the robot if left joystick is moved
            if ps5.control_request["reqLeftJoyMade"]:
                if current_time - motor_controller_last_check_time >= motor_controller_loop_interval:
                    move_robot(saber, ps5.control_request)
                    isMoving = True
                    motor_controller_last_check_time = time.time()
            else:
                if isMoving:
                    isMoving = False
                    saber.stop()

            # Reset PS5 request variables for next loop
            if ps5.control_request["reqMade"]:
                ps5.reset_controller_state()
                
            # Provide a brief sleep to allow worker threads to catch up to main loop
            time.sleep(.001)
            
            process_controller_events(ambient_routine)
            time.sleep(0.1)  # Small delay to avoid busy-waiting.
    except KeyboardInterrupt:
        print("Exiting ambient routine...")
    finally:
        pygame.joystick.quit()
        pygame.quit()
        saber.close()
        print("PS5 controller disconnected.")
        ambient_routine.stop()
        sound_ctrl.close()













# import os
# import time
# import random
# import subprocess
# import threading
# import queue
# from pydub import AudioSegment
# import pygame
# from usb_sound_controller import USB_SoundController
# 
# import spidev            # For SPI communications
# import RPi.GPIO as GPIO  # For controlling GPIO pins
# from PIL import Image, ImageDraw, ImageFont  # For image manipulation
# import math              # For geometric calculations
# from tft_display import TFTDisplay
# 
# from ambient_sound import AmbientSoundRoutine
# 
# import pygame
# import time
# from sabertooth import Sabertooth
# from ps5_controller import PS5_Controller
# 
# 
# class TFTRoutine:
#     def __init__(self, display, image_list):
#         """
#         bmp_list: List of at least 5 bmp file paths.
#         """
#         self.display = display
#         self.bmp_list = image_list
#         self.running = False  # Controls if the routine is active.
#         self.thread = None
#         self.lock = threading.Lock()
# 
#     def start(self):
#         with self.lock:
#             if not self.running:
#                 self.running = True
#                 # (Re)create and start the thread if not alive.
#                 self.thread = threading.Thread(target=self._run, daemon=True)
#                 self.thread.start()
#                 print("Image sound routine started.")
# 
#     def stop(self):
#         with self.lock:
#             if self.running:
#                 self.running = False
#                 print("Image sound routine suspended.")
# 
#     def _run(self):
#         while self.running:
#             # Choose a random play duration between 1 and 5 seconds.
#             play_duration = random.uniform(1, 5)
#             
#             # Choose a random sound file from the list.
#             bmp_file = random.choice(self.bmp_list)
#             print(f"Displaying: {bmp_file} for {play_duration:.2f} seconds")
#             
#             # Start playing the sound.
#             self.display.clear_screen("black")
#             self.display.display_bmp(bmp_file, position=(0, 0))
#             
#             # Wait for the random duration.
#             time.sleep(play_duration)
#             
#             # Stop the sound if it's still playing.
#             self.display.clear_screen("black")
# 
# # ---------------- PS5 Controller Handling ---------------- #
# def initialize_controller():
#     pygame.joystick.init()
#     if pygame.joystick.get_count() > 0:
#         controller = pygame.joystick.Joystick(0)
#         controller.init()
#         print(f"Controller '{controller.get_name()}' initialized.")
#         return controller
#     else:
#         print("No PS5 controller detected. Ambient routine control disabled.")
#         return None
# 
# def process_controller_events(ambient_routine):
#     """
#     Checks for PS5 controller events.
#     In this example, pressing button 0 toggles the ambient routine.
#     """
#     for event in pygame.event.get():
#         if event.type == pygame.JOYBUTTONDOWN:
#             # Toggle the ambient routine on button press (assume button 0).
#             if event.button == 0:
#                 if ambient_routine.running:
#                     ambient_routine.stop()
#                 else:
#                     ambient_routine.start()
# 
# def move_robot(saber, control_request):
#     # Sends motor commands to the Sabertooth motor controller.
#     speed = control_request["reqLeftJoyYValue"]
#     turn = control_request["reqLeftJoyXValue"]
#     saber.drive(speed, turn)
#     
# 
# # ---------------- Main Routine ---------------- #
# if __name__ == "__main__":
#     
#     GPIO.cleanup()
#     
#     # Initialize the sound controller.
#     sound_ctrl = USB_SoundController(volume=0.7)
#     display = TFTDisplay()
#     ps5 = PS5_Controller()
#     ps5.initialize_controller()
#     
#     # Initialize Sabertooth motor controller
#     saber = Sabertooth()
#     saber.set_ramping(21)  # Fast Ramping 1-10, Slow 11-20, Intermediate 21-80
#     isMoving = False
#     
#     ps5_last_check_time = time.time()
#     ps5_loop_interval = 0.02  # 20ms interval
#         
#     motor_controller_last_check_time = time.time()
#     motor_controller_loop_interval = 0.04  # 40ms interval
# 
#     # List of at least 5 different background ambient sounds.
#     ambient_sounds = [
#         "/home/ndrobotics/code/Pi Only Files /sounds/boxbox.mp3",
#         "/home/ndrobotics/code/Pi Only Files /sounds/f1.mp3",
#         "/home/ndrobotics/code/Pi Only Files /sounds/italiananthem.mp3",
#         "/home/ndrobotics/code/Pi Only Files /sounds/SmoothOperator.mp3",
#         "/home/ndrobotics/code/Pi Only Files /sounds/kimisteeringwheel.mp3"
#     ]
#     
#     image_list = [
#         "/home/ndrobotics/code/Pi Only Files /images/guido_1.bmp",
#         "/home/ndrobotics/code/Pi Only Files /images/guido_mog.bmp",
#         "/home/ndrobotics/code/Pi Only Files /images/guido_drill.bmp",
#         "/home/ndrobotics/code/Pi Only Files /images/guido_italy.bmp",
#         ]
# 
#     # Create the AmbientSoundRoutine instance.
#     ambient_routine = AmbientSoundRoutine(sound_ctrl, ambient_sounds)
#     display_routine = TFTRoutine(display, image_list)
# 
#     # Initialize PS5 controller (if available).
#     controller = initialize_controller()
# 
#     # Start the ambient routine by default.
#     ambient_routine.start()
#     display_routine.start()
# 
#     try:
#         # Main loop polls for controller events to toggle ambient sounds.
#         while True:
#             process_controller_events(ambient_routine)
#             time.sleep(0.1)  # Small delay to avoid busy-waiting.
#             
#             current_time = time.time()
# 
#             # Check PS5 controller state
#             if current_time - ps5_last_check_time >= ps5_loop_interval:
#                 pygame.event.pump()
#                 ps5.check_controls()
#                 ps5_last_check_time = current_time
# 
#             # Example: Use Arrow Up as a function call trigger
#             if ps5.control_request["reqArrowUp"]:
#                 print("This should call by function tied to Arrow Up")
# 
#             # Move the robot if left joystick is moved
#             if ps5.control_request["reqLeftJoyMade"]:
#                 if current_time - motor_controller_last_check_time >= motor_controller_loop_interval:
#                     move_robot(saber, ps5.control_request)
#                     isMoving = True
#                     motor_controller_last_check_time = time.time()
#             else:
#                 if isMoving:
#                     isMoving = False
#                     saber.stop()
# 
#             # Reset PS5 request variables for next loop
#             if ps5.control_request["reqMade"]:
#                 ps5.reset_controller_state()
#                 
#             # Provide a brief sleep to allow worker threads to catch up to main loop
#             time.sleep(.001)
#             
#     except KeyboardInterrupt:
#         print("Exiting ambient routine...")
#     finally:
#         ambient_routine.stop()
#         sound_ctrl.close()
#         pygame.joystick.quit()
#         pygame.quit()
#         saber.close()
#         display.close()
#         print("PS5 controller disconnected.")
        
        
