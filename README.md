# HeyItsGuido 

*Aka CSE40883 Introduction to Robotics course project CH1N*

**CH1N** is a multi-modal autonomous droid built using **Raspberry Pi 5**, **PiCamera2**, **PS5 controller**, and **TensorFlow**, inspired by *Cars* iconic character Guido and *Star Wars* droid naming convention.

It operates in three modes:

- **Manual Control** – via PS5 controller joystick input
- **Ambient and Themed Routines** – performs sequences with sound, LED and TFT display effects
- **Autonomous Navigation** – detects road signs and follows the lane on a mapped carpet track

## Hardware Components

### Core Electronics
- Raspberry Pi 5
- PiCamera 2
- PS5 DualSense Controller
- Sabertooth motor controller
- 2-channel Hi-Fi stereo amplifier
- Speakers × 2
- TFT display
- LED controller
- LED light × 24 (4 × 3 matrix × 2)
### Power and Wiring
- Sealed rechargeable lead-acid battery
- High-current automotive toggle switch
- Fuse block
- Terminal strip × 2
- Jumper wires
- Screws, washers, bolts, nuts, velcro, zip ties
### Actuators
- Rear drive motor × 2
- Rear wheel × 2
- Center wheel
- Mini servo × 2
- Motor mount channel × 2

## Software Stack

- **Python 3.11**
- **RealVNC** - remote desktop access
- **TensorFlow** - training and running visual recognition models
  - Object Detection API
  - Custom CNN Classifier (`.h5`)
- **OpenCV** – preprocessing image 
- **labelImg** - labeling image 
- **PiCamera2** – camera interface for Raspberry Pi
- **pygame** – joystick interface and sound effect
- **lgpio** – GPIO control
 
## Project Structure
```
CH1N/
├── code/             # All source code
├── design/           # Mechanical `.stl` files for 3D printing (not included)
├── pretrained_model/ # Download link in README
├── exported_model*/  # Trained TensorFlow models (not included)
├── dataset/          # Road sign and lane training/validation dataset of 500 images(not included)
├── tfod-env/         # Local virtual environment (not included)
├── README.md         # You're reading it
```

## Model and Training

- **Base model**: `ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8`
- **Fine-tuned** on a road sign and lane dataset of 500 images
- **CNN classifier** trained on cropped road sign images for higher precision

### Key Changes to `pipeline.config`:

- `num_classes` set to 5

- `batch_size` set to 8

- `num_steps` set to 1500

- `fine_tune_checkpoint_type` changed to `"detection"`

-  Added `load_all_detection_checkpoint_vars: false`

- `fine_tune_checkpoint` changed to `pretrained_model/checkpoint/ckpt-0`

- `train_input_path` changed to `dataset/train.record`

- `eval_input_path` changed to `dataset/val.record`

- `label_map_path` chanegd to `dataset/label_map.pbtxt`

## Setup Instructions

1. Clone the Repository
   
```text
git clone https://github.com/yuhanz07/HeyItsGuido.git
cd HeyItsGuido
```

2. Install Dependencies

```text
pip install -r requirements.txt
```

3. Download Pretrained Models and Train on Dataset

- [Download SSD MobileNet V2 FPNLite 320x320](http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8.tar.gz)
  
- [Download CNN Classifier (.h5)](https://your-google-drive-link)
