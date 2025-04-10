import cv2
from picamera2 import Picamera2
import time
import numpy as np
import threading
import pygame

from sabertooth import Sabertooth

# Global variable for sign recognition result
recognized_sign = None
stop_event = threading.Event()  # Event to signal threads to stop

def recognize_sign():
    """Thread function to perform image detection using Picamera2 and OpenCV."""
    global recognized_sign
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1024, 768)})
    picam2.configure(config)
    picam2.start()
    time.sleep(1)  # Allow camera to warm up

    while not stop_event.is_set() and recognized_sign is None:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         for cnt in contours:
#             area = cv2.contourArea(cnt)
#             if area < 300:
#                 continue
# 
#             # Approximate the contour to a polygon
#             peri = cv2.arcLength(cnt, True)
#             approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
# 
#             # Detect a Stop sign (example: hexagon)
#             if len(approx) == 6:
#                 recognized_sign = "STOP"
#                 print("Stop Sign Detected!")
#                 break
# 
#             # Detect an arrow (example: 7 to 12 sides)
#             elif 7 <= len(approx) <= 12:
#                 M = cv2.moments(cnt)
#                 if M["m00"] != 0:
#                     cx = int(M["m10"] / M["m00"])
#                 else:
#                     cx = 0
# 
#                 if cx < frame.shape[1] // 2:
#                     recognized_sign = "LEFT"
#                     print("Turn Left Detected!")
#                 else:
#                     recognized_sign = "RIGHT"
#                     print("Turn Right Detected!")
#                 break
#         for cnt in contours:
#             area = cv2.contourArea(cnt)
#             if area < 300:
#                 continue
# 
#             # Compute the center of the contour
#             M = cv2.moments(cnt)
#             if M["m00"] != 0:
#                 cx = int(M["m10"] / M["m00"])
#             else:
#                 continue  # skip this contour if center can't be computed
# 
#             # Skip contours not in the left half
#             if cx >= frame.shape[1] // 2:
#                 continue
# 
#             # Approximate the contour to a polygon
#             peri = cv2.arcLength(cnt, True)
#             approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
# 
#             # Detect a Stop sign (example: hexagon)
#             if len(approx) == 6:
#                 recognized_sign = "STOP"
#                 print("Stop Sign Detected!")
#                 break
# 
#             # Detect an arrow (example: 7 to 12 sides)
#             elif 7 <= len(approx) <= 12:
#                 recognized_sign = "LEFT"
#                 print("Turn Left Detected!")
#                 break

        # Load reference contour shapes for STOP and ARROW signs
        stop_sign_template   = cv2.imread("/home/ndrobotics/code/Pi Only Files /images/stop.jpg",0)
        left_arrow_template  = cv2.imread("/home/ndrobotics/code/Pi Only Files /images/left_arrow.jpg",0)
        right_arrow_template = cv2.imread("/home/ndrobotics/code/Pi Only Files /images/right_arrow.jpg",0)
        up_arrow_template    = cv2.imread("/home/ndrobotics/code/Pi Only Files /images/Up_Arrow.jpg",0)

        # Preprocess templates
        _, stop_thresh = cv2.threshold(stop_sign_template, 127, 255, cv2.THRESH_BINARY)
        _, left_arrow_thresh = cv2.threshold(left_arrow_template, 127, 255, cv2.THRESH_BINARY)
        _, right_arrow_thresh = cv2.threshold(right_arrow_template, 127, 255, cv2.THRESH_BINARY)
        _, up_arrow_thresh = cv2.threshold(up_arrow_template, 127, 255, cv2.THRESH_BINARY)

        # Find contours of the templates
        stop_contours, _ = cv2.findContours(stop_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        left_arrow_contours, _ = cv2.findContours(left_arrow_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        right_arrow_contours, _ = cv2.findContours(right_arrow_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        up_arrow_contours, _ = cv2.findContours(up_arrow_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        stop_cnt = max(stop_contours, key=cv2.contourArea)
        left_arrow_cnt = max(left_arrow_contours, key=cv2.contourArea)
        right_arrow_cnt = max(right_arrow_contours, key=cv2.contourArea)
        up_arrow_cnt = max(up_arrow_contours, key=cv2.contourArea)

        # In your frame processing loop:
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 300:
                continue

            # Match against the stop sign template
            stop_match = cv2.matchShapes(cnt, stop_cnt, cv2.CONTOURS_MATCH_I1, 0.0)
            left_arrow_match = cv2.matchShapes(cnt, left_arrow_cnt, cv2.CONTOURS_MATCH_I1, 0.0)
            right_arrow_match = cv2.matchShapes(cnt, right_arrow_cnt, cv2.CONTOURS_MATCH_I1, 0.0)
            up_arrow_match = cv2.matchShapes(cnt, up_arrow_cnt, cv2.CONTOURS_MATCH_I1, 0.0)
            
            # Skip contours not in the left half
#             if cx >= frame.shape[1] // 2:
#                 continue
# 
#             # Approximate the contour to a polygon
#             peri = cv2.arcLength(cnt, True)
#             approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            if stop_match < 0.15:  # Lower is better
                recognized_sign = "STOP"
                print("Stop Sign Detected!")
                break

            elif arrow_match < 0.2:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                else:
                    cx = 0

                if cx < frame.shape[1] // 2:
                    recognized_sign = "LEFT"
                    print("Turn Left Detected!")
                else:
                    recognized_sign = "RIGHT"
                    print("Turn Right Detected!")
                break



        time.sleep(0.5)  # Prevent excessive CPU usage

    picam2.stop()
    print("Image detection stopped.")

def process_controller_events():
    """Check for controller events and return True if the designated button is pressed."""
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            # For example, we start detection when button 0 is pressed.
            if event.button == 0:
                return True
    return False

def execute_action(saber, action):
    """Placeholder function to do something based on the recognized sign."""
    if action == "STOP":
        print("Executing STOP action.")
        # Add your STOP action code here
        stop_car(saber)
    
    elif action == "LEFT":
        print("Executing TURN LEFT action.")
        # Add your LEFT turn code here
        turn_left(saber)
        
    elif action == "RIGHT":
        print("Executing TURN RIGHT action.")
        # Add your RIGHT turn code here
        turn_right(saber)
        
def turn_right(saber):
    cur_time = time.time()
    while time.time() < cur_time + 1:
        saber.drive(-25, -50)
    
def turn_left(saber):
    cur_time = time.time()
    while time.time() < cur_time + 1:
        saber.drive(-25, 50)

def stop_car(saber):
    cur_time = time.time()
    while time.time() < cur_time + 1:
        saber.drive(0, 0)



if __name__ == "__main__":
    # Initialize pygame and the joystick
    saber = Sabertooth()
    #saber.set_ramping(21)  # Fast Ramping 1-10, Slow 11-20, Intermediate 21-80
#     isMoving = False
    
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        print("Controller initialized.")
    else:
        print("No controller found. Exiting.")
        pygame.quit()
        exit(1)

    try:
        while True:
            # Wait for a button press to trigger image detection
            if process_controller_events():
                print("Button pressed. Starting image detection...")
                # Reset state
                recognized_sign = None
                stop_event.clear()
                
                # Start the image recognition thread
                recognition_thread = threading.Thread(target=recognize_sign)
                recognition_thread.start()
                
                # Wait until a sign is recognized or the thread ends
                while recognition_thread.is_alive():
                    if recognized_sign is not None:
                        stop_event.set()  # Signal thread to stop if sign is detected
                        break
                    time.sleep(0.1)
                    saber.drive(-50,0)
                    
                recognition_thread.join()
                
                # Execute the action based on the recognized sign
                if recognized_sign:
                    print(f"Action recognized: {recognized_sign}")
                    execute_action(saber, recognized_sign)
                else:
                    print("No sign was recognized.")

                # Small delay to avoid multiple triggers from one press
                time.sleep(1)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting program...")
        stop_event.set()
    finally:
        pygame.quit()
        print("Program terminated.")

r