# import tensorflow as tf
# import cv2
# import numpy as np
# import os

# # Load model
# model = tf.keras.models.load_model("/Users/wanhoo/Documents/CSE40883/turn_classifier.h5")
# class_names = ['turnleft', 'turnright']  # must match your training order

# # Path to test images
# test_folder = "/Users/wanhoo/Documents/CSE40883/dataset/single_label_pic/turnright"

# for filename in os.listdir(test_folder):
#     if filename.endswith(".jpg") or filename.endswith(".png"):
#         image_path = os.path.join(test_folder, filename)
#         img = cv2.imread(image_path)
#         img_resized = cv2.resize(img, (64, 64))  # use the same input shape as training
#         img_normalized = img_resized.astype("float32") / 255.0
#         img_input = np.expand_dims(img_normalized, axis=0)

#         prediction = model.predict(img_input)
#         predicted_class = class_names[np.argmax(prediction[0])]
#         confidence = np.max(prediction[0])

#         print(f"{filename}: {predicted_class} ({confidence:.2f})")

#         # Show image with prediction
#         cv2.putText(img, f"{predicted_class} ({confidence:.2f})", (10, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#         cv2.imshow("Prediction", img)
#         cv2.waitKey(0)

# cv2.destroyAllWindows()


# import os
# import xml.etree.ElementTree as ET
# from collections import Counter

# # Path to your annotated dataset
# annotation_path = '/Users/wanhoo/Documents/CSE40883/dataset/captured_pic/'

# # Counter to store class occurrences
# class_counts = Counter()

# # Go through each .xml file
# for file in os.listdir(annotation_path):
#     if file.endswith('.xml'):
#         xml_path = os.path.join(annotation_path, file)
#         tree = ET.parse(xml_path)
#         root = tree.getroot()

#         for obj in root.findall('object'):
#             label = obj.find('name').text
#             class_counts[label] += 1

# # Print the result
# for label, count in class_counts.items():
#     print(f"{label}: {count}")

# # Optionally: bar chart
# try:
#     import matplotlib.pyplot as plt
#     labels = list(class_counts.keys())
#     values = list(class_counts.values())

#     plt.bar(labels, values)
#     plt.title('Class Distribution')
#     plt.xlabel('Class')
#     plt.ylabel('Count')
#     plt.grid(True, axis='y')
#     plt.show()
# except ImportError:
#     print("matplotlib not installed. Skipping chart.")

import os
import shutil
import xml.etree.ElementTree as ET

src_dir = '/Users/wanhoo/Documents/CSE40883/dataset/captured_pic/'
dst_dir = '/Users/wanhoo/Documents/CSE40883/dataset/yellowline/'

os.makedirs(dst_dir, exist_ok=True)

for file in os.listdir(src_dir):
    if file.endswith('.xml'):
        xml_path = os.path.join(src_dir, file)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        objects = root.findall('object')
        for obj in objects:
            name = obj.find('name').text
            if name != 'yellowline':
                root.remove(obj)

        # Only save if at least one yellowline label remains
        if root.findall('object'):
            # Save new XML
            new_xml_path = os.path.join(dst_dir, file)
            tree.write(new_xml_path)

            # Copy image too
            base_name = os.path.splitext(file)[0]
            jpg_src = os.path.join(src_dir, base_name + '.jpg')
            jpg_dst = os.path.join(dst_dir, base_name + '.jpg')
            if os.path.exists(jpg_src):
                shutil.copy(jpg_src, jpg_dst)

