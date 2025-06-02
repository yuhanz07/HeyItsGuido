import cv2
import os

# Set paths
input_folder = '/Users/wanhoo/Documents/CSE40883/dataset/new_pics'    # replace with your folder
output_folder = '/Users/wanhoo/Documents/CSE40883/dataset/new' # replace with your desired output folder

# Flip options: 1=horizontal, 0=vertical, -1=both
flip_code = 1  # change to 0 or -1 as needed

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process all images
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        img_path = os.path.join(input_folder, filename)
        img = cv2.imread(img_path)

        if img is not None:
            flipped = cv2.flip(img, flip_code)
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, flipped)
            print(f"Saved flipped image: {output_path}")
        else:
            print(f"Could not read: {img_path}")
