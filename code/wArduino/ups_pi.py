#!/usr/bin/env python3
import RPi.GPIO as GPIO
import os
import time

# Set up the GPIO pin for power detection
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN) 

STOP_FILE = "/tmp/stop_ups_monitor"  # Designated file for manual interrupt

def check_initial_power_state():
    """Wait 1 second and check if running on battery/supercapacitor (3V present)."""
    time.sleep(1)
    return GPIO.input(16) == GPIO.HIGH

def monitor_power():
    """Monitor power state and trigger shutdown on power loss.
       Also, exit if the STOP_FILE is detected.
    """
    try:
        while True:
            # If power is lost (0V), shut down
            if GPIO.input(16) == GPIO.LOW:
                os.system("sudo shutdown -h now")
                break

            # Check if manual stop file exists; if so, exit the loop
            if os.path.exists(STOP_FILE):
                break

            time.sleep(0.1)
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    if check_initial_power_state():
        monitor_power()
