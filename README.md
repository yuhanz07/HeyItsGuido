# CH1N
*CSE40883 Introduction to Robotics course project*

**CH1N** is a multi-modal autonomous droid built using **Raspberry Pi 5**, **PiCamera2**, **PS5 controller**, and **TensorFlow**, inspired by *Cars* iconic character Guido and *Star Wars* droid naming convention.

It operates in three modes:

- **Manual Control** – via PS5 controller joystick input
- **Ambient and Pre-programmed Routines** – performs sequences with sound, LED/TFT display effects
- **Autonomous Navigation** – detects road signs and follows a carpet track

## Hardware Used

- Raspberry Pi 5 (4GB)
- PiCamera 2
- TFT display (SPI)
- RGB LED matrix (optional)
- Mini speaker (for sound effects)
- PS5 DualSense Controller
- Motor driver (e.g., L298N)
- Carpet track with printed road signs

## Software Stack

- Python 3
- TensorFlow Lite (Object Detection + CNN Classifier)
- OpenCV
- PiCamera2
- Pygame (for sound)
- `evdev` or `pygame` joystick interface
- GPIO control via `lgpio` or `RPi.GPIO`
 
## Project Structure

CH1N/

├── code/ # All source code (main scripts, controllers, detection, UI)

├── design/ # Mechanical 3D printing design 

├── pretrained_model/ # Download link in README

├── exported_model*/ # Trained TensorFlow Lite models (not uploaded)

├── dataset/ # dataset of road sign and track (full set not included)

├── tfod-env/ # Local virtualenv (not included)

├── README.md # You're reading it!

## Modes and Features

### Manual Mode
- Left joystick → directional movement
- Buttons → triggers LED, sound, or visual effects
- TFT display shows current state or character expression

### Routine Mode
- Trigger pre-programmed action sequences
- Includes sound effects + LED/TFT visual animations

### Autonomous Mode
- Real-time road sign detection using PiCamera2 + TensorFlow Lite
- Recognizes: "Turn Left", "Turn Right", "Go Straight" and "Stop"
- Executes corresponding movement along a mapped carpet track
- CNN classifier improves reliability for visually ambiguous signs

## Model & Training

- **Base model**: `ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8`
- **Fine-tuned** on a custom sign dataset
- **CNN classifier** trained on cropped road sign images for higher precision

### Key Changes to `pipeline.config`:

```text
num_classes: 4
batch_size: 8
fine_tune_checkpoint: pretrained_model/checkpoint/ckpt-0
train_input_path: dataset/train.record
eval_input_path: dataset/val.record
label_map_path: dataset/label_map.pbtxt
```

## Setup Instructions

1. Clone the Repository
   
```text
git clone https://github.com/yourusername/guido-droid.git
cd guido-droid
```

2. Install Dependencies

```text
pip install -r requirements.txt
```

3. Download Models and Dataset

```text
🔗 Download pretrained detection model
🔗 Download CNN classifier .h5
pretrained_model/
models/
```

