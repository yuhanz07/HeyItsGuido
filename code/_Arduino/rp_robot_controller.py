############################################################
#
#            Raspberry Pi Robot Controller
#            Revised: 12/14/2024
#            ND: Introduction to Robotics
#            Professor McLaughlin
#
############################################################
import pygame
import time
from smbus2 import SMBus
import serial
import threading

# Setup I2C comms channel for PS5 Controller
I2C_BUS = 1  # I2C bus number (typically 1 on Raspberry Pi)
I2C_ADDRESS = 0x08  # I2C address of the Arduino Mega ADK

# Setup serial comms for all other messages
serial_port = "/dev/ttyAMA0"    # Points to the serial PINs on Raspberry Pi
baud_rate = 115200              # Set baud rate

# Initialize Pygame and the joystick module
pygame.init()
pygame.joystick.init()
firstMessage = True
stop_event = threading.Event() # Used to gracefully stop threads on program exit

# Define debounce time for PS5 controller inputs in seconds
debounce_time = 0.5

# Joystick Control Variables
joystickLeftSending = False
joystickRightSending = False

# Helper function to debounce PS5 controller buttons
last_press_time = {}

# Wait for joystick to connect before allowing all other robot functions
while pygame.joystick.get_count() == 0:
    if firstMessage:
        print("Waiting for a joystick to connect...")
        firstMessage = False
        
    event = pygame.event.wait()

    if event.type == pygame.JOYDEVICEADDED:
        pygame.joystick.init()

# Initialize the serial connection for all non-PS5 comms
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Serial port {serial_port} opened at {baud_rate} baud.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")

# I2C is used exclusively for the PS5 Controller - use send_serial_message for everything else
def send_i2c_PS5_data(bus, data):
    """
    Sends data via I2C.
    :param data: Data string to send
    """
    try:
        # Convert the string to bytes and send it
        bus.write_i2c_block_data(I2C_ADDRESS, 0x00, [ord(char) for char in data])
        print(f"Sent via I2C: {data}")
    except Exception as e:
        print(f"Error sending data: {e}")

# Used to send all non-PS5 data to the Arduino - appends '%' to all messages for consistent terminator
def send_serial_message(ser, message):
    try:
        # Add the terminator '%'
        full_message = message + "%"

        # Send the message over serial
        ser.write(full_message.encode('utf-8'))
        print(f"Sent via Serial: {full_message}")

    except serial.SerialException as e:
        print(f"Error sending message: {e}")

# Used to debounce repeated PS5 controller inputs
def is_debounced(key):
    current_time = time.time()
    if key not in last_press_time or (current_time - last_press_time[key] > debounce_time):
        last_press_time[key] = current_time
        return True
    return False

# Used to send any PS5 controller inputs to the Arduino
def check_controls(joystick):
    global joystickLeftSending
    global joystickRightSending
    # Check buttons
    with SMBus(I2C_BUS) as bus:
        if joystick.get_button(0) and is_debounced(0):
            print("Button Cross pressed.")
            send_i2c_PS5_data(bus, "BTN00%")
            
        if joystick.get_button(1) and is_debounced(1):
            print("Button Circle pressed.")
            send_i2c_PS5_data(bus, "BTN01%")

        if joystick.get_button(2) and is_debounced(2):
            print("Button Triangle pressed.")
            send_i2c_PS5_data(bus, "BTN02%")
            
        if joystick.get_button(3) and is_debounced(3):
            print("Button Square pressed.")
            send_i2c_PS5_data(bus, "BTN03%")

        if joystick.get_button(4) and is_debounced(4):
            print("Button L1 pressed.")
            send_i2c_PS5_data(bus, "BTN04%")

        if joystick.get_button(5) and is_debounced(5):
            print("Button R1 pressed.")
            send_i2c_PS5_data(bus, "BTN05%")

        if joystick.get_button(6) and is_debounced(6):
            print("Button L2 pressed.")
            send_i2c_PS5_data(bus, "BTN06%")

        if joystick.get_button(7) and is_debounced(7):
            print("Button R2 pressed.")
            send_i2c_PS5_data(bus, "BTN07%")

        if joystick.get_button(8) and is_debounced(8):
            print("Button Share pressed.")
            send_i2c_PS5_data(bus, "BTN08%")

        if joystick.get_button(9) and is_debounced(9):
            print("Button Options pressed.")
            send_i2c_PS5_data(bus, "BTN09%")

        if joystick.get_button(10) and is_debounced(10):
            print("Button PS Button pressed.")
            send_i2c_PS5_data(bus, "BTN10%")

        if joystick.get_button(11) and is_debounced(11):
            print("Button Left Joystick Button (L3) pressed.")
            send_i2c_PS5_data(bus, "BTN11%")

        if joystick.get_button(12) and is_debounced(12):
            print("Button Right Joystick Button (R3) pressed.")
            send_i2c_PS5_data(bus, "BTN12%")

        # Check D-pad (hat switch)
        hat = joystick.get_hat(0)
        if hat == (0, 1) and is_debounced(13):
            print("Button Arrow_Up pressed.")
            send_i2c_PS5_data(bus, "BTN13%")

        if hat == (0, -1) and is_debounced(14):
            print("Button Arrow_Down pressed.")
            send_i2c_PS5_data(bus, "BTN14%")

        if hat == (-1, 0) and is_debounced(15):
            print("Button Arrow_Left pressed.")
            send_i2c_PS5_data(bus, "BTN15%")

        if hat == (1, 0) and is_debounced(16):
            print("Button Arrow_Right pressed.")
            send_i2c_PS5_data(bus, "BTN16%")

        # Check left joystick
        lx = joystick.get_axis(0)
        ly = joystick.get_axis(1)
        
        if abs(lx) > 0.1 or abs(ly) > 0.1:
            joystickLeftSending = True
            lxInt = int(lx * 100)
            lyInt = int(ly * 100)
            
            if lxInt < 0:
                signXString = "-"
            else:
                signXString = "+"
                
            if lyInt < 0:
                signYString = "-"
            else:
                signYString = "+"
                
            lxInt = abs(lxInt)
            lyInt = abs(lyInt)
                
            # Convert the joystick range of values to a convienent Sabertooth motor controller value range
            lxInt = map_integer(lxInt, 0, 100, 0, 127)
            lyInt = map_integer(lyInt, 0, 100, 0, 127)
            
            sendString = "JL" + signXString + f"{lxInt:03}" + "#" + signYString + f"{lyInt:03}" + "%"
            print("Joystick Left data sent: " + sendString)
            send_i2c_PS5_data(bus, sendString)
        
        else:
        
            if joystickLeftSending == True:
                joystickLeftSending = False
                sendString = "JLSTOP%"
                print("Joystick Left data sent: " + sendString)
                send_i2c_PS5_data(bus, sendString)
            
       # Check right joystick
        rx = joystick.get_axis(3)
        ry = joystick.get_axis(4)
        if abs(rx) > 0.1 or abs(ry) > 0.1:
            joystickRightSending = True
            rxInt = int(rx * 100)
            ryInt = int(ry * 100)

            if rxInt < 0:
                signXString = "-"
            else:
                signXString = "+"
                
            if ryInt < 0:
                signYString = "-"
            else:
                signYString = "+"
                
            rxInt = abs(rxInt)
            ryInt = abs(ryInt)
                
            # Convert the joystick range of values to a convienent Sabertooth motor controller value range
            rxInt = map_integer(rxInt, 0, 100, 0, 127)
            ryInt = map_integer(ryInt, 0, 100, 0, 127)

            sendString = "JR" + signXString + f"{rxInt:03}" + "#" + signYString + f"{ryInt:03}" + "%"
            print("Joystick Right data sent: " + sendString)
            send_i2c_PS5_data(bus, sendString)
            
        
        else:
        
            if joystickRightSending == True:
                joystickRightSending = False
                sendString = "JRSTOP%"
                print("Joystick Right data sent: " + sendString)
                send_i2c_PS5_data(bus, sendString)

def map_integer(value, old_min, old_max, new_min, new_max):
    # Ensure the old range is valid
    if old_max - old_min == 0:
        raise ValueError("Old range cannot be zero")
    
    # Map the value to the new range
    mapped_value = new_min + (value - old_min) * (new_max - new_min) / (old_max - old_min)
    
    # Round the result to ensure it's an integer
    return round(mapped_value)
            
def PS5_controller_loop():
    global stop_event
    # Initialize the PS5 controller
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Detected joystick: {joystick.get_name()}")
    
    last_check_time = time.time()
    loop_interval = 0.005  # 5ms interval    
    
    while True:
        pygame.event.pump()
        current_time = time.time()
        if current_time - last_check_time >= loop_interval:
            last_check_time = current_time
            check_controls(joystick)
                
        if stop_event.is_set():
            break

def inbound_serial_loop():
    global stop_event
    inboundBuffer = ""

    while True:
        data = ser.read().decode('utf-8', errors='ignore')
        if data:
            inboundBuffer += data
            # Check if the message ends with '%'
            if inboundBuffer.endswith('%'):
                print("Received message:", inboundBuffer[:-1])  # Print message without '%'

                # Check for Arduino send back mesage
                if inboundBuffer[: -1] == "SysLive":
                    print("Arduino is live and sending back data")
                                
                # Check your additional messages here and set your state variables

                inboundBuffer = ""  # Clear the buffer for the next message
                
        if stop_event.is_set():
            break
    
# Main Processing Loop for the robot
def main():
    try:
        # Let the Arduino know we are running
        send_serial_message(ser, "SysLive")
        time.sleep(1)
        global stop_event
                   
        PS5_process_thread = threading.Thread(target = PS5_controller_loop, daemon=True)
        inbound_serial_thread = threading.Thread(target = inbound_serial_loop, daemon=True)

        # Check the PS5 controller and throttle to Arduino every .02 seconds
        PS5_process_thread.start()
        # Check for inbound serial messages
        inbound_serial_thread.start()
        
        while True:
           # Waiting while robotic thread routines run
           do_nothing = True
            
    except KeyboardInterrupt:
        print("Exiting program...")

    finally:
        # Cleanup
        stop_event.set()
        PS5_process_thread.join()
        inbound_serial_thread.join()
        pygame.joystick.quit()
        pygame.quit()
        ser.close()
        print("PS5 controller disconnected.")

if __name__ == "__main__":
    main()