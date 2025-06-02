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

class LEDController:
    def __init__(self):
        # Hard-coded pin assignments.
        self.SIN_PIN = 23    # Data input
        self.SCLK_PIN = 24   # Serial clock
        self.XLAT_PIN = 25   # Latch signal
        
        # List of pins used (for selective cleanup).
        self._used_pins = [self.SIN_PIN, self.SCLK_PIN, self.XLAT_PIN]
        
        # Hard-coded number of LEDs.
        self.num_leds = 24
        # Initialize LED states: all off.
        self.led_states = [0.0] * self.num_leds
        
        # Gamma value for brightness correction.
        self.gamma = 2.2
        
        self.bit_delay = 0.0001  # 100 microseconds; adjust this value as needed.
        
        # Initialize GPIO.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SIN_PIN, GPIO.OUT)
        GPIO.setup(self.SCLK_PIN, GPIO.OUT)
        GPIO.setup(self.XLAT_PIN, GPIO.OUT)
        
        # Set initial output levels to low.
        GPIO.output(self.SIN_PIN, 0)
        GPIO.output(self.SCLK_PIN, 0)
        GPIO.output(self.XLAT_PIN, 0)
        
        # Create command queue and start the worker thread.
        self.command_queue = queue.Queue()
        self.shutdown_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
        # On initialization, update the board with all LEDs off.
        self.send()
    
    def set_led(self, position, intensity):
        # Queue a command to update the LED at 'position' to the given 'intensity'.
        # Intensity must be a float between 0.0 (off) and 1.0 (full brightness).
        if not (0 <= position < self.num_leds):
            raise ValueError(f"LED position {position} is out of range (0 to {self.num_leds - 1}).")
        if not (0.0 <= intensity <= 1.0):
            raise ValueError("Intensity must be between 0.0 and 1.0.")
        self.command_queue.put(('set_led', position, intensity))
    
    def set_leds(self, led_intensity_map):
        # Queue a command to update multiple LEDs.
        #
        # :param led_intensity_map: A dict mapping LED positions to intensity values.
        self.command_queue.put(('set_leds', led_intensity_map))
    
    def send(self):
        # Queue a command to update the board with the current LED state matrix.
        self.command_queue.put(('send',))
    
    def _worker(self):
        # Worker thread that processes queued commands in the order they were received.
        # Expected commands:
        #  - ('set_led', position, intensity)
        #  - ('set_leds', led_intensity_map)
        #  - ('send',)
        while not self.shutdown_event.is_set():
            try:
                command = self.command_queue.get(timeout=0.1)
                if command[0] == 'set_led':
                    _, pos, intensity = command
                    self.led_states[pos] = intensity
                elif command[0] == 'set_leds':
                    _, led_map = command
                    for pos, intensity in led_map.items():
                        if not (0 <= pos < self.num_leds):
                            raise ValueError(f"LED position {pos} is out of range (0 to {self.num_leds - 1}).")
                        if not (0.0 <= intensity <= 1.0):
                            raise ValueError("Intensity must be between 0.0 and 1.0.")
                        self.led_states[pos] = intensity
                elif command[0] == 'send':
                    self._update_board()
                self.command_queue.task_done()
            except queue.Empty:
                continue  # No command available; loop again.
    
    def _update_board(self):
        # Convert LED intensities to 12-bit values (using gamma correction) and send 288 bits (MSB-first per channel)
        # to the TLC5947 via bit-banging. Then, pulse XLAT to latch the data.
        # Apply gamma correction and convert intensities (0.0 - 1.0) to 12-bit integers (0 - 4095).
        pwm_values = [int((val ** self.gamma) * 4095) for val in self.led_states]
        
        # Build bitstream: channel 23 first, down to channel 0; each channel is 12 bits (MSB-first).
        bitstream = ""
        for value in reversed(pwm_values):
            bits = format(value, '012b')
            bitstream += bits
        
        # Shift out each bit.
        for bit in bitstream:
            GPIO.output(self.SIN_PIN, int(bit))
            GPIO.output(self.SCLK_PIN, 1)
            time.sleep(self.bit_delay)  # Small delay; adjust as needed.
            GPIO.output(self.SCLK_PIN, 0)
            time.sleep(self.bit_delay)
        
        # Pulse XLAT to latch the data into the outputs.
        GPIO.output(self.XLAT_PIN, 1)
        time.sleep(self.bit_delay)
        GPIO.output(self.XLAT_PIN, 0)
    
    def close(self):
        # Gracefully shut down the worker thread, clear the command queue,
        # and clean up only the GPIO pins used by this class.
        self.shutdown_event.set()
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
                self.command_queue.task_done()
            except queue.Empty:
                break
        self.worker_thread.join()
        GPIO.cleanup(self._used_pins)
        print("LEDController Shutdown complete.")

class Eyes_Control:
    def look_left(controller):
        controller.set_leds({
            0:1, 1:1, 2:1,
            3:1, 4:1, 5:0,
            6:1, 7:1, 8:0,
            9:1, 10:1, 11:1,
            12:1, 13:1, 14:0,
            15:1, 16:1, 17:0
        })
        controller.send()
    
    def look_right(controller):
        controller.set_leds({
            0:1, 1:1, 2:1,
            3:0, 4:1, 5:1,
            6:0, 7:1, 8:1,
            9:1, 10:1, 11:1,
            12:0, 13:1, 14:1,
            15:0, 16:1, 17:1
        })
        controller.send()

    def close_eyes(controller):
        controller.set_leds({  # <-- CHANGED
            0:1, 1:0, 2:1,
            3:0, 4:1, 5:0,
            6:1, 7:.5, 8:1,
            9:1, 10:0, 11:1,
            12:0, 13:1, 14:0,
            15:1, 16:0, 17:1
        })
        controller.send()

    def full_eyes(controller):
        controller.set_leds({  # <-- CHANGED
            0:1, 1:.5, 2:1,
            3:.5, 4:1, 5:.5,
            6:1, 7:.5, 8:1,
            9:1, 10:.5, 11:1,
            12:.5, 13:1, 14:.5,
            15:1, 16:.5, 17:1
        })
        controller.send()
        
    def sad_eyes(controller):
        controller.set_leds({  # <-- CHANGED
            0:0, 1:.1, 2:0,
            3:.1, 4:.3, 5:.1,
            6:.1, 7:.3, 8:.3,
            9:0, 10:.1, 11:0,
            12:.1, 13:.3, 14:.1,
            15:.3, 16:.3, 17:.3
        })
        controller.send()

# Test suite when the module is executed directly.
if __name__ == '__main__':
    print("Starting LEDController test suite...\n")
    controller = LEDController()
    
    try:
        x_count = 1
        while(1):
            Eyes_Control.full_eyes(controller)
            time.sleep(.5)
            Eyes_Control.look_right(controller)
            time.sleep(.5)
            Eyes_Control.look_left(controller)
            time.sleep(.5)
            Eyes_Control.close_eyes(controller)
            time.sleep(.5)
            
    finally:
        controller.close()
    
    print("\nLEDController test suite complete.")
