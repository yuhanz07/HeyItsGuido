import RPi.GPIO as GPIO
import time
import threading

class gesture:
    def __init__(self, servo_pin=18):
        GPIO.setmode(GPIO.BCM)
        self.servo_pin = servo_pin
        GPIO.setup(self.servo_pin, GPIO.OUT)
        
        # 50Hz PWM for servo
        self.pwm = GPIO.PWM(self.servo_pin, 50)
        self.pwm.start(0)
        print(f"Gesture servo initialized on GPIO {servo_pin}")

    def set_angle(self, angle):
        """Set the servo to a specific angle (0-180)."""
        duty = angle / 18 + 2
        GPIO.output(self.servo_pin, True)
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        GPIO.output(self.servo_pin, False)
        self.pwm.ChangeDutyCycle(0)

    def open_mouth(self):
        self.set_angle(180)
    
    def talk(self):
        self.set_angle(180)
        time.sleep(0.5)
        self.set_angle(0)
        time.sleep(0.5)
    
    def close(self):
        self.pwm.stop()
        GPIO.cleanup(self.servo_pin)
        print("Gesture servo stopped.")







          
