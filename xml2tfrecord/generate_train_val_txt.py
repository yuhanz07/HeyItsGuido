import os
from sklearn.model_selection import train_test_split

# Path to your annotations
annotation_dir = "/Users/wanhoo/Documents/CSE40883/code/Pi Only Files/captured_pic"

# Path to output folder (can be anywhere you like)
output_dir = "/Users/wanhoo/Documents/CSE40883/code/xml2tfrecord"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get all XML files and strip extensions
all_xml = [f for f in os.listdir(annotation_dir) if f.endswith('.xml')]
base_filenames = [os.path.splitext(f)[0] for f in all_xml]

# Split
train_files, val_files = train_test_split(base_filenames, train_size=0.8, random_state=42)

# Write train.txt
train_txt_path = os.path.join(output_dir, "train.txt")
with open(train_txt_path, "w") as f:
    f.writelines([f"{name}\n" for name in train_files])

# Write val.txt
val_txt_path = os.path.join(output_dir, "val.txt")
with open(val_txt_path, "w") as f:
    f.writelines([f"{name}\n" for name in val_files])

print(f"train.txt and val.txt saved to: {output_dir}")

