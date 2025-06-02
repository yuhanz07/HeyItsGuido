import os
import time
import random
import subprocess
import threading
import queue
from pydub import AudioSegment
import pygame
from usb_sound_controller import USB_SoundController

import spidev            # For SPI communications
import RPi.GPIO as GPIO  # For controlling GPIO pins
from PIL import Image, ImageDraw, ImageFont  # For image manipulation
import math              # For geometric calculations
from tft_display import TFTDisplay

from led_eyes4x3 import LEDController
from led_eyes4x3 import Eyes_Control

# Define TFT display pins (GPIO numbers) based on your wiring.
TFT_CS_PIN = 5     # Chip Select (GPIO5)
TFT_RESET_PIN = 6  # Reset (GPIO6)
TFT_DC_PIN = 26    # Data/Command (GPIO26)

# Display specifications for the 1.8" TFT (ST7735R):
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160

class AmbientLEDRoutine:
    def __init__(self, ledcontroller):
        self.ledcontroller = ledcontroller
        self.running = False  # Controls if the routine is active.
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                # (Re)create and start the thread if not alive.
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()
                print("LED routine started.")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                print("LED routine suspended.")
                
    def _run(self):
        while self.running:
            # Choose a random play duration between 5 and 10 seconds.
            eye_choice = random.randint(1, 9)
            play_duration = random.uniform(.5, 4)
            
            match eye_choice:
                case 1:
                    Eyes_Control.look_right(self.ledcontroller)
                case 2:
                    Eyes_Control.look_left(self.ledcontroller)
                case 3:
                    Eyes_Control.close_eyes(self.ledcontroller)
                case 4:
                    Eyes_Control.full_eyes(self.ledcontroller)
                case 5:
                    Eyes_Control.forward_eyes_f(self.ledcontroller)
                case 6:
                    Eyes_Control.sad_eyes(self.ledcontroller)
                case 7:
                    Eyes_Control.dead_eyes(self.ledcontroller)
                case 8:
                    Eyes_Control.dazed_eyes(self.ledcontroller)
                case 9:
                    Eyes_Control.happy_eyes(self.ledcontroller)
        
            # Wait for the random duration.
            time.sleep(play_duration)
            

    
# ---------------- Ambient Sound Routine ---------------- #
class AmbientSoundRoutine:
    def __init__(self, sound_controller, sound_list):
        """
        sound_controller: Instance of USB_SoundController.
        sound_list: List of at least 5 sound file paths.
        """
        self.sound_controller = sound_controller
        self.sound_list = sound_list
        self.running = False  # Controls if the routine is active.
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                # (Re)create and start the thread if not alive.
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()
                print("Ambient sound routine started.")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                print("Ambient sound routine suspended.")

    def _run(self):
        while self.running:
            # Choose a random play duration between 5 and 10 seconds.
            play_duration = random.uniform(5, 10)
            
            # Choose a random sound file from the list.
            sound_file = random.choice(self.sound_list)
            print(f"Playing: {sound_file} for {play_duration:.2f} seconds")
            
            # Start playing the sound.
            self.sound_controller.play_audio(sound_file)
            
            # Wait for the random duration.
            time.sleep(play_duration)
            
            # Stop the sound if it's still playing.
            self.sound_controller.stop_sound()

            
class TFTRoutine:
    def __init__(self, display, image_list):
        """
        bmp_list: List of at least 5 bmp file paths.
        """
        self.display = display
        self.bmp_list = image_list
        self.running = False  # Controls if the routine is active.
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                # (Re)create and start the thread if not alive.
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()
                print("Image sound routine started.")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                print("Image sound routine suspended.")

    def _run(self):
        while self.running:
            # Choose a random play duration between 1 and 5 seconds.
            play_duration = random.uniform(1, 5)
            
            # Choose a random sound file from the list.
            bmp_file = random.choice(self.bmp_list)
            print(f"Displaying: {bmp_file} for {play_duration:.2f} seconds")
            
            # Start playing the sound.
            self.display.clear_screen("black")
            self.display.display_bmp(bmp_file, position=(0, 0))
            
            # Wait for the random duration.
            time.sleep(play_duration)
            
            # Stop the sound if it's still playing.
            self.display.clear_screen("black")


# ---------------- PS5 Controller Handling ---------------- #
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

# ---------------- Main Routine ---------------- #
if __name__ == "__main__":
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
    ambient_s_routine = AmbientSoundRoutine(sound_ctrl, ambient_sounds)

    # Initialize PS5 controller (if available).
    controller = initialize_controller()

    # Start the ambient routine by default.
    ambient_s_routine.start()
    
    display = TFTDisplay()
    
    image_list = [
        "/home/ndrobotics/code/Pi Only Files /images/guido_1.bmp",
        "/home/ndrobotics/code/Pi Only Files /images/guido_mog.bmp",
        "/home/ndrobotics/code/Pi Only Files /images/guido_drill.bmp",
        "/home/ndrobotics/code/Pi Only Files /images/guido_italy.bmp",
        ]
    
    display_routine = TFTRoutine(display, image_list)
 
    display_routine.start()
    
    ledcontroller = LEDController()
    
    led_routine = AmbientLEDRoutine(ledcontroller)

    led_routine.start()

    try:
        # Main loop polls for controller events to toggle ambient sounds.
        while True:
            process_controller_events(ambient_s_routine,display_routine,led_routine)
            time.sleep(0.1)  # Small delay to avoid busy-waiting.
    except KeyboardInterrupt:
        print("Exiting ambient routine...")
    finally:
        ambient_routine.stop()
        sound_ctrl.close()
