import os
import time
import random
import subprocess
import threading
import queue
from pydub import AudioSegment
import pygame
from usb_sound_controller import USB_SoundController

from sabertooth import Sabertooth
from ps5_controller import PS5_Controller

import spidev            # For SPI communications
import RPi.GPIO as GPIO  # For controlling GPIO pins
import lgpio
from PIL import Image, ImageDraw, ImageFont  # For image manipulation
import math              # For geometric calculations
from tft_display import TFTDisplay

from led_eyes4x3 import LEDController
from led_eyes4x3 import Eyes_Control

from ambient_routines import AmbientLEDRoutine
from ambient_routines import AmbientSoundRoutine
from ambient_routines import TFTRoutine

from routine_move import routine_move

import ShowRoutine1
import PitStopRoutine
import SpinSignRoutine

from gesture import gesture

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

def process_controller_events(ambient_routine1,ambient_routine2,ambient_routine3):
    """
    Checks for PS5 controller events.
    In this example, pressing button 0 toggles the ambient routine.
    """
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            # Toggle the ambient routine on button press (assume button 0).
            if event.button == 0:
                if ambient_routine1.running:
                    ambient_routine1.stop()
                    ambient_routine2.stop()
                    ambient_routine3.stop()
                
                else:
                    ambient_routine1.start()
                    ambient_routine2.start()
                    ambient_routine3.start()


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
        "/home/ndrobotics/code/Pi Only Files /sounds/italiananthem.mp3",
        "/home/ndrobotics/code/Pi Only Files /sounds/SmoothOperator.mp3",
        "/home/ndrobotics/code/Pi Only Files /R1_Files/Italian_music.mp3",
        "/home/ndrobotics/code/Pi Only Files /R1_Files/bolt.mp3",
        "/home/ndrobotics/code/Pi Only Files /R1_Files/guidotalk.mp3",
        "/home/ndrobotics/code/Pi Only Files /GudioRoutine1/stop1_a.mp3",
        "/home/ndrobotics/code/Pi Only Files /GudioRoutine1/stop2_a.mp3",
        "/home/ndrobotics/code/Pi Only Files /GudioRoutine1/stop3_a.mp3",
        "/home/ndrobotics/code/Pi Only Files /GudioRoutine2/shake1a.mp3",
        "/home/ndrobotics/code/Pi Only Files /GudioRoutine2/shake2a.mp3",
        "/home/ndrobotics/code/Pi Only Files /GudioRoutine2/shake4a.mp3",
    ]

    # Create the AmbientSoundRoutine instance.
    ambientsoundroutine = AmbientSoundRoutine(sound_ctrl, ambient_sounds)

    # Initialize PS5 controller (if available).
    controller = initialize_controller()

    # Start the ambient routine by default.
    ambientsoundroutine.start()
    
    # Start display
    display = TFTDisplay()
    
    image_list = [
        "/home/ndrobotics/code/Pi Only Files /images/guido_1.bmp",
        "/home/ndrobotics/code/Pi Only Files /images/guido_mog.bmp",
        "/home/ndrobotics/code/Pi Only Files /images/guido_drill.bmp",
        "/home/ndrobotics/code/Pi Only Files /R1_Files/drinks.bmp",
        "/home/ndrobotics/code/Pi Only Files /R1_Files/Guido_drive.bmp",
        "/home/ndrobotics/code/Pi Only Files /R1_Files/sad.bmp",
        "/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop1_1.bmp",
        "/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop2_1.bmp",
        "/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop4.bmp",
        "/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake1_1.bmp",
        "/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake3_2.bmp",
        "/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake5_4.bmp"
        ]
    
    ambientdisplayroutine = TFTRoutine(display, image_list)
 
    ambientdisplayroutine.start()
    
    # LED
    ledcontroller = LEDController()
    
    ambientledroutine = AmbientLEDRoutine(ledcontroller)

    ambientledroutine.start()
    
    # gesture
    motor1 = gesture(18)
    motor2 = gesture(15)
    
    #movement
    move = routine_move()
    
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
            if ps5.control_request["reqSquare"]:
                print("Routine 1")
                ShowRoutine1.showroutine1(move, ledcontroller, display,sound_ctrl, motor1, motor2)
                
            if ps5.control_request["reqTriangle"]:
                print("PitStopRoutine")
                PitStopRoutine.pitstoproutine(move,ledcontroller,display,sound_ctrl,motor1, motor2)

            if ps5.control_request["reqCircle"]:
                print("SpinSignRoutine")
                SpinSignRoutine.spinsignroutine(move,ledcontroller,display,sound_ctrl)


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
            
            process_controller_events(ambientsoundroutine, ambientledroutine, ambientdisplayroutine)
            time.sleep(0.1)  # Small delay to avoid busy-waiting.
    except KeyboardInterrupt:
        print("Exiting ambient routine...")
    finally:
        pygame.joystick.quit()
        pygame.quit()
        saber.close()
        print("PS5 controller disconnected.")
        ambientsoundroutine.stop()
        ambientledroutine.stop()
        ambientdisplayroutine.stop()
        sound_ctrl.close()
        display.close()
        ledcontroller.close()
