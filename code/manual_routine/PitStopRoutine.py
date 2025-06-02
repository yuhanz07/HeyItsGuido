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
from gesture import forklift
import time
from usb_sound_controller import USB_SoundController

# Define TFT display pins (GPIO numbers) based on your wiring.
TFT_CS_PIN = 5     # Chip Select (GPIO5)
TFT_RESET_PIN = 6  # Reset (GPIO6)
TFT_DC_PIN = 26    # Data/Command (GPIO26)

# Display specifications for the 1.8" TFT (ST7735R):
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160


def stop1pics(display):
    for _ in range(4):
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop1_1.bmp", position=(0, 0))
        time.sleep(.66)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop1_2.bmp", position=(0, 0))
        time.sleep(.66)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop1_3.bmp", position=(0, 0))
        time.sleep(.66)
    
def stop1eyes(ledcontroller):
    for _ in range(16):
        Eyes_Control.forward_eyes_f(ledcontroller)
        time.sleep(.5)
    

def stop2pics(display):
    for _ in range(4):
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop2_1.bmp", position=(0, 0))
        time.sleep(.66)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop2_2.bmp", position=(0, 0))
        time.sleep(.66)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop2_3.bmp", position=(0, 0))
        time.sleep(.66)

def stop2eyes(ledcontroller):
    Eyes_Control.look_left(ledcontroller)
    time.sleep(3)
    Eyes_Control.look_right(ledcontroller)
    time.sleep(3.5)
    Eyes_Control.forward_eyes_f(ledcontroller)
    time.sleep(1.5)
    
def stop2audio(sound_ctrl):
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop2_a.mp3")
    time.sleep(4)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop2_a.mp3")
    time.sleep(4)
    sound_ctrl.stop_sound()

def stop3pics(display):
    for _ in range(3):
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop3_1.bmp", position=(0, 0))
        time.sleep(.66)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop3_2.bmp", position=(0, 0))
        time.sleep(.66)
        display.clear_screen("black")
        display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop3_3.bmp", position=(0, 0))
        time.sleep(.66)
        
def stop3eyes(ledcontroller):
    for _ in range(6):
        Eyes_Control.blink2(ledcontroller, .5)
        

def stop4eyes(ledcontroller):
    Eyes_Control.look_right(ledcontroller)
    time.sleep(.5)
    Eyes_Control.look_left(ledcontroller)
    time.sleep(.5)
    Eyes_Control.happy_eyes(ledcontroller)
    time.sleep(4)

           
def stop1(move,ledcontroller,display,sound_ctrl):
    #display
    disp_thread = threading.Thread(target=stop1pics, args=(display,))
    disp_thread.start()
    
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop1_a.mp3")
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=stop1eyes, args=(ledcontroller,))
    led_thread.start()
    #motion
    time.sleep(4)
    move.move_forward(speed=40, duration=4)
    sound_ctrl.stop_sound()
    
    disp_thread.join()
    led_thread.join()
#     gesture_thread.join()

def stop2(move,ledcontroller,display,sound_ctrl,motor1,motor2):
    #display
    disp_thread = threading.Thread(target=stop2pics, args=(display,))
    disp_thread.start()
    
    #gesture
    forklift.forward(motor1, motor2)
    
    # audio
    sound_thread = threading.Thread(target=stop2audio, args=(sound_ctrl,))
    sound_thread.start()
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=stop2eyes, args=(ledcontroller,))
    led_thread.start()
    #motion
    move.move_backward(speed=40, duration=1.5)
    move.turn_left(speed=40, duration=1.5)
    move.move_forward(speed=60, duration=2)
    move.turn_right(speed=40, duration=1.5)
    move.move_forward(speed=40, duration=1.5)
    
    disp_thread.join()
    sound_thread.join()
    led_thread.join()
#     gesture_thread.join()
    
def stop3(move,ledcontroller,display,sound_ctrl,motor1, motor2):
    #display
    disp_thread = threading.Thread(target=stop3pics, args=(display,))
    disp_thread.start()
    
    forklift.backward(motor1, motor2)
    
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop3_a.mp3")
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=stop3eyes, args=(ledcontroller,))
    led_thread.start()
    #motion
    move.drive(-50,-30,2)
    move.turn_right(40,2)
    move.move_forward(speed=40, duration=2)
    
    disp_thread.join()
    led_thread.join()
#     gesture_thread.join()

def stop4(move,ledcontroller,display,sound_ctrl):
    #display
    display.clear_screen("black")
    display.display_bmp("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop4.bmp", position=(0, 0))    
    # audio
    sound_ctrl.set_volume(0.5)
    sound_ctrl.play_audio("/home/ndrobotics/code/Pi Only Files /GuidoRoutine1/stop4_a.mp3")
    # gesture
#     gesture_thread = threading.Thread(target=gesture_routine.open_mouth)
#     gesture_thread.start()
    # led
    led_thread = threading.Thread(target=stop4eyes, args=(ledcontroller,))
    led_thread.start()
    #motion
    time.sleep(1)
    move.turn_right(40,2.3)
    move.turn_left(40,2.3)
    
    led_thread.join()
#     gesture_thread.join()

def pitstoproutine(move,ledcontroller,display,sound_ctrl,motor1, motor2):
    stop1(move,ledcontroller,display,sound_ctrl)
    stop2(move,ledcontroller,display,sound_ctrl,motor1, motor2)
    time.sleep(.5)
    stop3(move,ledcontroller,display,sound_ctrl,motor1, motor2)
    time.sleep(.5)
    stop4(move,ledcontroller,display,sound_ctrl)
    

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
    # gesture
    motor1 = gesture(18)
    motor2 = gesture(15)
    
    try:
        pitstoproutine(move,ledcontroller,display,sound_ctrl,motor1, motor2)
            
  
    finally:
        ledcontroller.close()
        move.close()
        sound_ctrl.close()
        display.close()

    
    print("\nLEDController test suite complete.")