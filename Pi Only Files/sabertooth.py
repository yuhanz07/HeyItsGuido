################################################################
# Motor Controller Class for ND Robotics Course
# 3-7-2025
# Professor McLaughlin
################################################################
import serial
import time
import multiprocessing
import queue

class Sabertooth:
    def __init__(self, port='/dev/ttyAMA0', baudrate=9600, address=128, max_queue_size=100):
        self.address = address
        self.running = multiprocessing.Value('b', True)
        self.max_queue_size = max_queue_size  

        try:
            self.ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
        except Exception as e:
            print(f"Serial Port Error: {e}")
            return

        self.command_queue = multiprocessing.Queue(maxsize=self.max_queue_size)

        self.process = multiprocessing.Process(target=self.process_commands)
        self.process.start()

        time.sleep(2)

        self.set_auto_stop(200)
        self.set_deadband(5)

    def send_command(self, command, value):
        # Sends a properly formatted packetized serial command to the Sabertooth
        if not (0 <= value <= 127):
            raise ValueError("Value must be between 0 and 127")

        address_byte = int(self.address)  
        command_byte = int(command)  
        data_byte = int(value)  
        checksum = (address_byte + command_byte + data_byte) & 0x7F  

        packet = bytes([address_byte, command_byte, data_byte, checksum])

        self.ser.write(packet)
        self.ser.flush()

    def process_commands(self):
        while True:
            if not self.running.value:
                break
            
            try:
                packet = self.command_queue.get(timeout=0.01)
                self.ser.write(packet)
                self.ser.flush()
            except queue.Empty:
                pass
        
            time.sleep(0.005)

    def drive(self, speed, turn):
        # Convert speed (-127 to 127) to Sabertooth expected format (0 to 127)
        if speed >= 0:
            speed_value = self.map_integer(speed, 0, 127, 0, 127)  # Map positive speed for forward
            self.send_command(8, speed_value)  # Drive forward
        else:
            speed_value = self.map_integer(abs(speed), 0, 127, 0, 127)  # Map negative speed for backward
            self.send_command(9, speed_value)  # Drive backward

        # Convert turn (-127 to 127) to Sabertooth expected format (0 to 127)
        if turn >= 0:
            turn_value = self.map_integer(turn, 0, 127, 0, 127)  # Map positive turn for right
            self.send_command(10, turn_value)  # Turn right
        else:
            turn_value = self.map_integer(abs(turn), 0, 127, 0, 127)  # Map negative turn for left
            self.send_command(11, turn_value)  # Turn left

    def stop(self):
        self.send_command(8, 0)  # Stop forward
        self.send_command(9, 0)  # Stop backward
        self.send_command(10, 0)  # Stop right turn
        self.send_command(11, 0)  # Stop left turn

    def set_auto_stop(self, timeout_ms):
        # Sets the serial timeout period. This determines how long the motor driver will wait 
        # without receiving a command before shutting off.
        #
        # - timeout_ms: Time in milliseconds (100ms units, range: 0-12700ms).
        # - Setting 0 disables the timeout.
        value = min(max(int(timeout_ms / 100), 0), 127)  # Scale timeout in 100ms units
        self.send_command(14, value)

    def set_ramping(self, ramp_value):
        # Sets the acceleration ramping rate to control motor smoothness.
        #
        # - 1-10: Fast ramping (default: 1 = 1/4 sec ramp, 2 = 1/8 sec ramp, etc.).
        # - 11-20: Slow ramping.
        # - 21-80: Intermediate ramping.
        #
        # This setting persists through a power cycle.
        if not (1 <= ramp_value <= 80):
            raise ValueError("Ramping value must be between 1 and 80.")
        
        self.send_command(16, ramp_value)
        
    def set_deadband(self, deadband_value):
        # Sets the deadband range for motor activation.
        #          
        # - Default: 3 (motors stop between speed commands 124-131).
        # - Higher values increase the dead zone.
        # - 0 resets to default.
        # 
        # This setting persists through a power cycle.
        if not (0 <= deadband_value <= 127):
            raise ValueError("Deadband value must be between 0 and 127.")
                    
        self.send_command(17, deadband_value)
       
    def close(self):
        self.running.value = False
        self.process.join(timeout=1)
        self.ser.close()

    @staticmethod
    def map_integer(value, old_min, old_max, new_min, new_max):
        if old_max - old_min == 0:
            raise ValueError("Old range cannot be zero")
        return round(new_min + (value - old_min) * (new_max - new_min) / (old_max - old_min))
