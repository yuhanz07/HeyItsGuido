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
from led_eyes4x3 import LEDController
from led_eyes4x3 import Eyes_Control
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


def shake1pics(display):
    for _ in range(3):
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake1_1.bmp", position=(0, 0))
        time.sleep(1.5)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake1_2.bmp", position=(0, 0))
        time.sleep(1.5)
    
def shake1eyes(ledcontroller):
    for _ in range(2):
        Eyes_Control.look_left(ledcontroller)
        time.sleep(1)
        Eyes_Control.look_right(ledcontroller)
        time.sleep(1)
        Eyes_Control.close_eyes(ledcontroller)
        time.sleep(2.5)
    

def shake2pics(display):
    for _ in range(1):
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake2_1.bmp", position=(0, 0))
        time.sleep(2)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake2_2.bmp", position=(0, 0))
        time.sleep(2)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake2_3.bmp", position=(0, 0))
        time.sleep(2)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake2_4.bmp", position=(0, 0))
        time.sleep(2)

def shake2eyes(ledcontroller):
    for _ in range(5):
        Eyes_Control.forward_eyes_f(ledcontroller)
        time.sleep(1)
    Eyes_Control.happy_eyes(ledcontroller)
    time.sleep(3)
    
    
def shake2audio(sound_ctrl):
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake2a.mp3")
    time.sleep(8.5)
    sound_ctrl.stop_sound()

def shake3pics(display):
    for _ in range(3):
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake3_1.bmp", position=(0, 0))
        time.sleep(.66)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake3_2.bmp", position=(0, 0))
        time.sleep(.66)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake3_3.bmp", position=(0, 0))
        time.sleep(.66)
        
def shake3eyes(ledcontroller):
    for _ in range(5):
        Eyes_Control.dazed_eyes(ledcontroller)
        time.sleep(1)

def shake4pics(display):
    for _ in range(4):
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake4_1.bmp", position=(0, 0))
        time.sleep(.5)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake4_2.bmp", position=(0, 0))
        time.sleep(.5)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake4_3.bmp", position=(0, 0))
        time.sleep(.5)

def shake4eyes(ledcontroller):
    Eyes_Control.full_eyes(ledcontroller)
    time.sleep(1.5)
    Eyes_Control.close_eyes(ledcontroller)
    time.sleep(1.5)
    Eyes_Control.look_left(ledcontroller)
    time.sleep(1.5)
    Eyes_Control.look_right(ledcontroller)
    time.sleep(1.5)

def shake5pics(display):
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake5_1.bmp", position=(0, 0))
    time.sleep(1)
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake5_2.bmp", position=(0, 0))
    time.sleep(1)
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake5_3.bmp", position=(0, 0))
    time.sleep(1)
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake5_4.bmp", position=(0, 0))
    time.sleep(1)
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake5_5.bmp", position=(0, 0))
    time.sleep(1)
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake5_6.bmp", position=(0, 0))
    time.sleep(2)


def shake5eyes(ledcontroller):
    for _ in range(10):
        Eyes_Control.forward_eyes_f(ledcontroller)
        time.sleep(.5)
    Eyes_Control.happy_eyes(ledcontroller)
    time.sleep(2)
           
def shake1(move,ledcontroller,display,sound_ctrl):
    #display
    disp_thread = threading.Thread(target=shake1pics, args=(display,))
    disp_thread.start()
    
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake1a.mp3")
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=shake1eyes, args=(ledcontroller,))
    led_thread.start()
    #motion
    move.drive(20, 10, 4.5)
    move.drive(-20, -10, 4.5)
    sound_ctrl.stop_sound()
    
    disp_thread.join()
    led_thread.join()
#     gesture_thread.join()

def shake2(move,ledcontroller,display,sound_ctrl):
    #display
    disp_thread = threading.Thread(target=shake2pics, args=(display,))
    disp_thread.start()
    
    # audio
    sound_thread = threading.Thread(target=shake2audio, args=(sound_ctrl,))
    sound_thread.start()
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=shake2eyes, args=(ledcontroller,))
    led_thread.start()
#     #motion
    move.turn_left(speed=30, duration=1.5)
    move.move_forward(speed=30, duration=1)
    move.turn_right(speed=30, duration=3)
    move.move_forward(speed=30, duration=2.5)
#     
    disp_thread.join()
    sound_thread.join()
    led_thread.join()
#     gesture_thread.join()
    
def shake3(move,ledcontroller,display,sound_ctrl):
    #display
    disp_thread = threading.Thread(target=shake3pics, args=(display,))
    disp_thread.start()
    
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake3a.mp3")
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=shake3eyes, args=(ledcontroller,))
    led_thread.start()
    #motion
    move.turn_right(40, 5)
    
    disp_thread.join()
    led_thread.join()
#     gesture_thread.join()

def shake4(move,ledcontroller,display,sound_ctrl):
    #display
    disp_thread = threading.Thread(target=shake4pics, args=(display,))
    disp_thread.start()   
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake4a.mp3")
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=shake4eyes, args=(ledcontroller,))
    led_thread.start()
    #motion
    move.turn_left(40,1.5)
    move.move_backward(50, 2)
    move.turn_left(40,1.5)
    move.move_forward(50, 1)
    
    disp_thread.join()
    led_thread.join()
#     gesture_thread.join()

def shake5(move,ledcontroller,display,sound_ctrl):
    #display
    disp_thread = threading.Thread(target=shake5pics, args=(display,))
    disp_thread.start()   
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine2/shake5a.mp3")
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=shake5eyes, args=(ledcontroller,))
    led_thread.start()
    #motion
    move.turn_right(50,1)
    move.turn_left(50,1)
    move.turn_right(50,1)
    move.move_backward(60, 1)
    move.move_forward(60, 1)
    move.drive(-20, 10, 2)
    
    disp_thread.join()
    led_thread.join()
#     gesture_thread.join()

def spinsignroutine(move,ledcontroller,display,sound_ctrl):
    shake1(move,ledcontroller,display,sound_ctrl)
    shake2(move,ledcontroller,display,sound_ctrl)
    shake3(move,ledcontroller,display,sound_ctrl)
    shake4(move,ledcontroller,display,sound_ctrl)
    shake5(move,ledcontroller,display,sound_ctrl)
    


# Test suite when the module is executed directly.
if __name__ == '__main__':
    print("Starting...\n")
    #movement
    move = routine_move()
    # led controller
    ledcontroller = LEDController()
    # Start display
    display = TFTDisplay()
    # Initialize the sound controller.
    sound_ctrl = USB_SoundController(volume=0.7)
    
    try:
        shake1(move,ledcontroller,display,sound_ctrl)
        shake2(move,ledcontroller,display,sound_ctrl)
        shake3(move,ledcontroller,display,sound_ctrl)
        shake4(move,ledcontroller,display,sound_ctrl)
        shake5(move,ledcontroller,display,sound_ctrl)
         
  
    finally:
        ledcontroller.close()
        move.close()
        sound_ctrl.close()
        display.close()

    
    print("\nLEDController test suite complete.")