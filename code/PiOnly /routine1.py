################################################################
# LED Controller for ND Robotics Course
# 3-7-2025
# Professor McLaughlin
################################################################
import threading
import queue
import time
import RPi.GPIO as GPIO
import random
from led_eyes import LEDController
from led_eyes import Eyes_Control
from tft_display import TFTDisplay
from tft_display import TFTRoutine
from routine_move import routine_move
from gesture import gesture
import time
from usb_sound_controller import USB_SoundController

# Define TFT display pins (GPIO numbers) based on your wiring.
TFT_CS_PIN = 5     # Chip Select (GPIO5)
TFT_RESET_PIN = 6  # Reset (GPIO6)
TFT_DC_PIN = 26    # Data/Command (GPIO26)

# Display specifications for the 1.8" TFT (ST7735R):
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160

def blinking_routine(ledcontroller):
    """Blink the eyes while the robot is moving."""
    start_time = time.time()
    while time.time() - start_time < 2:  # Adjust to match driving duration
        Eyes_Control.full_eyes(ledcontroller)
        time.sleep(0.5)
        Eyes_Control.close_eyes(ledcontroller)
        time.sleep(0.5)
    
def look_LR(ledcontroller):
    start_time = time.time()
    while time.time() - start_time < 2:  # Adjust to match driving duration
        Eyes_Control.look_right(ledcontroller)
        time.sleep(0.5)
        Eyes_Control.look_left(ledcontroller)
        time.sleep(0.5)
    
    
def move_forward_rt(move, ledcontroller, display,sound_ctrl):
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /R1_Files/Guido_Drive.bmp", position=(1, 0))
        
    # Start blinking in a thread
    blink_thread = threading.Thread(target=blinking_routine, args=(ledcontroller,))
    blink_thread.start()
    
    gesture_thread = threading.Thread(target=gesture_routine.talk)
    gesture_thread.start()
    
    # audio
    sound_ctrl.set_volume(1)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /R1_Files/guidotalk.mp3")
    
    # Move forward at the same time
    move.move_forward(speed=40, duration=4)
    
    # Wait for blinking to finish
    blink_thread.join()
    gesture_thread.join()
    
def move_left_rt(move, ledcontroller, display, sound_ctrl):
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /R1_Files/SpinningSign.bmp", position=(1, 0))
        
    # Start blinking in a thread
    lr_thread = threading.Thread(target=look_LR, args=(ledcontroller,))
    lr_thread.start()
    
    # audio
    sound_ctrl.set_volume(1)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /R1_Files/Italian_music.mp3")
    
    # Move forward at the same time
    move.turn_left(speed=15, duration=4)
    
    sound_ctrl.stop_sound()
    
#     time.sleep()
    
    # Wait for blinking to finish
    lr_thread.join()
    
def move_left_rt2(move, ledcontroller, display, sound_ctrl):
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /R1_Files/SpinningSign.bmp", position=(1, 0))
        
    # Start blinking in a thread
    lr_thread = threading.Thread(target=look_LR, args=(ledcontroller,))
    lr_thread.start()
    
    # audio
    sound_ctrl.set_volume(1)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /R1_Files/Italian_music.mp3")
    
    # Move forward at the same time
    move.turn_left(speed=30, duration=1.8)
    
    sound_ctrl.stop_sound()
    
#     time.sleep()
    
    # Wait for blinking to finish
    lr_thread.join()



def move_right_rt(move, ledcontroller, display, sound_ctrl):
    #display
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /R1_Files/SpinningSign.bmp", position=(1, 0))
        
    # led
    lr_thread = threading.Thread(target=look_LR, args=(ledcontroller,))
    lr_thread.start()
    
    # audio
    sound_ctrl.set_volume(1)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /R1_Files/Italian_music.mp3")
    
#     time.sleep(3)
    
    # Move forward at the same time
    move.turn_right(speed=15, duration=5)
    
    # Wait for blinking to finish
    lr_thread.join()

def sad_rt(move, ledcontroller, display, sound_ctrl):
    #display
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /R1_Files/sad.bmp", position=(1, 0))
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /R1_Files/sad_violin.mp3")
    # led
    Eyes_Control.sad_eyes(ledcontroller)
    #motion
    move.move_forward(speed=25, duration=3)
    move.turn_left(speed=25, duration=3)
    sound_ctrl.stop_sound()
    
def drink_rt(move, ledcontroller, display, sound_ctrl):
    #display
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /R1_Files/drinks.bmp", position=(1, 0))
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /R1_Files/bar_scene.mp3")
    # gesture
    gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
    gesture_thread.start()
    # led
    Eyes_Control.full_eyes(ledcontroller)
    #motion
    move.move_forward(speed=40, duration=3)
    
    gesture_thread.join()
           

# Test suite when the module is executed directly.
if __name__ == '__main__':
    print("Starting...\n")
    move = routine_move()
    ledcontroller = LEDController()
    gesture_routine = gesture(servo_pin=18)
    
    # Start display
    display = TFTDisplay()
    # Initialize the sound controller.
    sound_ctrl = USB_SoundController(volume=0.7)
    
    try:
        x_count = 1
        while(1):
            for _ in range(4):
                move_forward_rt(move, ledcontroller, display,sound_ctrl)
                move_left_rt(move, ledcontroller, display,sound_ctrl)
                sad_rt(move, ledcontroller, display, sound_ctrl)
                move_right_rt(move, ledcontroller, display,sound_ctrl)
                drink_rt(move, ledcontroller, display, sound_ctrl)
                move_left_rt2(move, ledcontroller, display, sound_ctrl)
                
                
#                 # Start blinking in a thread
#                 blink_thread = threading.Thread(target=blinking_routine, args=(ledcontroller,))
#                 blink_thread.start()
# 
#                 # Move forward at the same time
#                 move.move_forward(speed=50, duration=2)
# 
#                 # Wait for blinking to finish
#                 blink_thread.join()
# 
#                 # Small delay before turning
#                 time.sleep(2)
# 
#                 move.turn_left(speed=50, duration=1)
#                 time.sleep(2)
    
#     try:
#         x_count = 1
#         while(1):
#             Eyes_Control.full_eyes(controller)
#             time.sleep(.5)
#             Eyes_Control.look_right(controller)
#             time.sleep(.5)
#             Eyes_Control.look_left(controller)
#             time.sleep(.5)
#             Eyes_Control.close_eyes(controller)
#             time.sleep(.5)
#             
#             # Move in a 1m x 1m square
#             for _ in range(4):
#                 move.move_forward(speed=50, duration=2)  # adjust duration based on your robot's speed
#                 move.turn_left(speed=50, duration=1)  # 90 degree left turn
            
    finally:
        ledcontroller.close()
        move.close()
        sound_ctrl.close()
        gesture.close()
    
    print("\nLEDController test suite complete.")