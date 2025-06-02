################################################################
# TFT Display Class for ND Robotics Course
# 3-7-2025
# Professor McLaughlin
################################################################
import spidev            # For SPI communications
import RPi.GPIO as GPIO  # For controlling GPIO pins
import threading         # For managing threads
import time              # For sleep/delay functions
from PIL import Image, ImageDraw, ImageFont  # For image manipulation
import math              # For geometric calculations
from queue import Queue  # For thread-safe queue

# Define TFT display pins (GPIO numbers) based on your wiring.
TFT_CS_PIN = 5     # Chip Select (GPIO5)
TFT_RESET_PIN = 6  # Reset (GPIO6)
TFT_DC_PIN = 26    # Data/Command (GPIO26)

# Display specifications for the 1.8" TFT (ST7735R):
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160

class TFTDisplay:
    # Class to control a 1.8" TFT display (128x160, 18-bit color) using the ST7735R driver.
    #
    # All drawing functions are enqueued and processed sequentially by a dedicated worker thread.
    #  
    # A threading.Lock is used to protect access to the shared image buffer.
    def __init__(self):
        # Set up GPIO.
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(TFT_CS_PIN, GPIO.OUT)
        GPIO.setup(TFT_RESET_PIN, GPIO.OUT)
        GPIO.setup(TFT_DC_PIN, GPIO.OUT)
        # Ensure CS starts high.
        GPIO.output(TFT_CS_PIN, GPIO.HIGH)

        # Initialize SPI.
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 4000000  # 4 MHz for reliability.
        self.spi.mode = 0

        # Create an image buffer using Pillow.
        self.image = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), "black")
        self.draw = ImageDraw.Draw(self.image)

        # Lock to synchronize access to the image buffer.
        self.lock = threading.Lock()

        # Create a Queue to manage drawing tasks.
        self.queue = Queue()

        # Initialize a list to hold additional threads if needed.
        self.threads = []

        # Start the worker thread that processes the queue.
        self.worker_thread = threading.Thread(target=self._queue_worker, daemon=True)
        self.worker_thread.start()

        # Run display initialization.
        self._initialize_display()

    def _queue_worker(self):
        # Continuously process tasks from the queue
        while True:
            task = self.queue.get()
            if task is None:
                self.queue.task_done()
                break  # Sentinel value received; exit the worker.
            func, args, kwargs = task
            with self.lock:
                func(*args, **kwargs)
            self.queue.task_done()

    def _enqueue(self, func, *args, **kwargs):
        # Enqueue a drawing task
        self.queue.put((func, args, kwargs))

    def _send_command(self, cmd):
        # Send a command byte with manual CS control
        GPIO.output(TFT_CS_PIN, GPIO.LOW)
        GPIO.output(TFT_DC_PIN, GPIO.LOW)  # Command mode.
        self.spi.xfer2([cmd])
        GPIO.output(TFT_CS_PIN, GPIO.HIGH)

    def _send_data(self, data):
        # Send data bytes with manual CS control
        GPIO.output(TFT_CS_PIN, GPIO.LOW)
        GPIO.output(TFT_DC_PIN, GPIO.HIGH)  # Data mode.
        if isinstance(data, list):
            self.spi.xfer2(data)
        else:
            self.spi.xfer2([data])
        GPIO.output(TFT_CS_PIN, GPIO.HIGH)

    def _set_address_window(self, x0, y0, x1, y1):
        # Set the address window for pixel data
        self._send_command(0x2A)  # Column Address Set.
        self._send_data([0x00, x0, 0x00, x1])
        self._send_command(0x2B)  # Row Address Set.
        self._send_data([0x00, y0, 0x00, y1])
        self._send_command(0x2C)  # Memory Write.

    def _initialize_display(self):
        # Initialize the display using the ST7735R sequence
        GPIO.output(TFT_RESET_PIN, GPIO.LOW)
        time.sleep(0.15)
        GPIO.output(TFT_RESET_PIN, GPIO.HIGH)
        time.sleep(0.15)

        self._send_command(0x01)  # Software reset.
        time.sleep(0.5)

        self._send_command(0x11)  # Sleep out.
        time.sleep(0.5)

        self._send_command(0x3A)  # Color mode.
        self._send_data(0x06)     # 18-bit color.
        time.sleep(0.1)

        self._send_command(0x36)  # MADCTL.
        self._send_data(0xC8)     # Classic orientation.
        time.sleep(0.1)

        self._send_command(0x29)  # Display ON.
        time.sleep(0.5)

        # Clear screen with blue for test.
        self.clear_screen("blue")

    def _update_display(self):
        # Update the physical display with the current image buffer
        self._set_address_window(0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1)
        raw_data = self.image.tobytes("raw", "RGB")
        chunk_size = 4096
        GPIO.output(TFT_CS_PIN, GPIO.LOW)
        GPIO.output(TFT_DC_PIN, GPIO.HIGH)
        for i in range(0, len(raw_data), chunk_size):
            self.spi.xfer2(list(raw_data[i:i+chunk_size]))
        GPIO.output(TFT_CS_PIN, GPIO.HIGH)

    # Task functions that perform the drawing operations.
    def _task_clear_screen(self, color):
        self.draw.rectangle([0, 0, SCREEN_WIDTH, SCREEN_HEIGHT], fill=color)
        self._update_display()

    def _task_draw_text(self, text, position, font_size, color):
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        self.draw.text(position, text, fill=color, font=font)
        self._update_display()

    def _task_display_bmp(self, bmp_path, position):
        try:
            bmp_image = Image.open(bmp_path)
            bmp_image = bmp_image.convert("RGB")
            self.image.paste(bmp_image, position)
            self._update_display()
        except Exception as e:
            print("Error displaying BMP:", e)

    def _task_draw_box(self, top_left, bottom_right, line_color, fill_color):
        if fill_color:
            self.draw.rectangle([top_left, bottom_right], outline=line_color, fill=fill_color)
        else:
            self.draw.rectangle([top_left, bottom_right], outline=line_color)
        self._update_display()

    def _task_draw_circle(self, center, radius, line_color, fill_color):
        x, y = center
        bbox = [x - radius, y - radius, x + radius, y + radius]
        self.draw.ellipse(bbox, outline=line_color, fill=fill_color)
        self._update_display()

    def _task_draw_line(self, start, end, line_width, color):
        self.draw.line([start, end], fill=color, width=line_width)
        self._update_display()

    def _task_draw_arrow(self, arrow_color, thickness, direction):
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        if direction == "up":
            points = [(w/2, h*0.1), (w*0.1, h*0.9), (w*0.5, h*0.7), (w*0.9, h*0.9)]
        elif direction == "down":
            points = [(w/2, h*0.9), (w*0.1, h*0.1), (w*0.5, h*0.3), (w*0.9, h*0.1)]
        elif direction == "left":
            points = [(w*0.1, h/2), (w*0.9, h*0.1), (w*0.7, h/2), (w*0.9, h*0.9)]
        elif direction == "right":
            points = [(w*0.9, h/2), (w*0.1, h*0.1), (w*0.3, h/2), (w*0.1, h*0.9)]
        else:
            print("Invalid direction for arrow. Use up, down, left, or right.")
            return
        self.draw.polygon(points, fill=arrow_color, outline=arrow_color)
        if thickness > 1:
            for i in range(1, thickness):
                offset_points = [(x+i, y+i) for (x, y) in points]
                self.draw.polygon(offset_points, outline=arrow_color)
        self._update_display()

    def _task_draw_octagon(self, center, size, line_color, fill_color):
        cx, cy = center
        points = []
        for i in range(8):
            angle = math.radians(45 * i - 22.5)
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            points.append((x, y))
        self.draw.polygon(points, outline=line_color, fill=fill_color)
        self._update_display()

    # Public drawing methods that enqueue tasks.
    def clear_screen(self, color="black"):
        self._enqueue(self._task_clear_screen, color)

    def draw_text(self, text, position=(0, 0), font_size=20, color=(255, 255, 255)):
        self._enqueue(self._task_draw_text, text, position, font_size, color)

    def display_bmp(self, bmp_path, position=(0, 0)):
        self._enqueue(self._task_display_bmp, bmp_path, position)

    def draw_box(self, top_left, bottom_right, line_color=(255, 255, 255), fill_color=None):
        self._enqueue(self._task_draw_box, top_left, bottom_right, line_color, fill_color)

    def draw_circle(self, center, radius, line_color=(255, 255, 255), fill_color=None):
        self._enqueue(self._task_draw_circle, center, radius, line_color, fill_color)

    def draw_line(self, start, end, line_width=2, color=(255, 255, 255)):
        self._enqueue(self._task_draw_line, start, end, line_width, color)

    def draw_arrow(self, arrow_color=(255, 255, 255), thickness=3, direction="up"):
        self._enqueue(self._task_draw_arrow, arrow_color, thickness, direction)

    def draw_octagon(self, center, size, line_color=(255, 255, 255), fill_color=None):
        self._enqueue(self._task_draw_octagon, center, size, line_color, fill_color)

    def start_non_blocking_demo(self, func, *args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        self.threads.append(t)
        return t

    def close(self):
        # Signal the worker thread to exit by enqueuing a sentinel.
        self.queue.put(None)
        self.worker_thread.join(timeout=5)
        # Wait for any additional threads.
        for t in self.threads:
            t.join(timeout=5)
        self.spi.close()
        time.sleep(1)
        try:
            GPIO.cleanup([TFT_CS_PIN, TFT_RESET_PIN, TFT_DC_PIN])
        except Exception as e:
            print("GPIO cleanup error:", e)
        print("Display closed gracefully.")

###############################
# Test Routine
###############################
if __name__ == '__main__':
    display = TFTDisplay()
    try:
        print("Clearing screen to black...")
        display.clear_screen("black")
        time.sleep(1)
        
        print("Drawing text in various sizes...")
        display.clear_screen("black")
        display.draw_text("Small Text", position=(5, 5), font_size=12, color=(255, 255, 0))
        time.sleep(1)
        display.clear_screen("black")
        display.draw_text("Medium Text", position=(5, 20), font_size=18, color=(0, 255, 255))
        time.sleep(1)
        display.clear_screen("black")
        display.draw_text("Large Text", position=(5, 40), font_size=24, color=(255, 0, 255))
        time.sleep(1)
        
        print("Drawing box with fill and outline...")
        display.clear_screen("black")
        display.draw_box(top_left=(5, 5), bottom_right=(120, 60), line_color=(0, 255, 0), fill_color=(0, 0, 255))
        time.sleep(1)
        
        print("Drawing circle (outline only)...")
        display.clear_screen("black")
        display.draw_circle(center=(64, 80), radius=40, line_color=(255, 255, 255))
        time.sleep(1)
        
        print("Drawing circle (filled)...")
        display.clear_screen("black")
        display.draw_circle(center=(64, 80), radius=40, line_color=(255, 255, 255), fill_color=(255, 0, 0))
        time.sleep(1)
        
        print("Drawing radiating lines from center...")
        display.clear_screen("black")
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            end_x = int(center[0] + 60 * math.cos(rad))
            end_y = int(center[1] + 60 * math.sin(rad))
            display.draw_line(start=center, end=(end_x, end_y), line_width=1, color=(0, 255, 0))
        time.sleep(2)
        
        print("Drawing arrow pointing up...")
        display.clear_screen("black")
        display.draw_arrow(arrow_color=(255, 255, 0), thickness=4, direction="up")
        time.sleep(2)
        
        print("Drawing arrow pointing right...")
        display.clear_screen("black")
        display.draw_arrow(arrow_color=(255, 0, 255), thickness=4, direction="right")
        time.sleep(2)
        
        print("Drawing octagon...")
        display.clear_screen("black")
        display.draw_octagon(center=(64, 80), size=40, line_color=(255, 255, 255), fill_color=(0, 128, 128))
        time.sleep(2)
        
        print("Displaying BMP image...")
        display.clear_screen("black")
        display.display_bmp("test.bmp", position=(0, 70))
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        display.close()
