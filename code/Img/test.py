# test_detection.py
import cv2
import numpy as np
import os
# import glob
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

# Load saved model
PATH_TO_MODEL = "/Users/wanhoo/Documents/CSE40883/exported_model/saved_model"
PATH_TO_LABELS = "/Users/wanhoo/Documents/CSE40883/dataset/label_map.pbtxt"
PATH_TO_IMAGE = "/Users/wanhoo/Documents/CSE40883/dataset/captured_pic/test1.jpg"

detect_fn = tf.saved_model.load(PATH_TO_MODEL)

# Load label map
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# Load image
image_np = cv2.imread(PATH_TO_IMAGE)
input_tensor = tf.convert_to_tensor(image_np)[tf.newaxis, ...]

# Run detection
detections = detect_fn(input_tensor)

# Visualize
viz_utils.visualize_boxes_and_labels_on_image_array(
    image_np,
    detections['detection_boxes'][0].numpy(),
    detections['detection_classes'][0].numpy().astype(np.int32),
    detections['detection_scores'][0].numpy(),
    category_index,
    use_normalized_coordinates=True,
    line_thickness=3,
    min_score_thresh=0.3  
)

print("Scores:", detections['detection_scores'][0].numpy()[:5])
print("Boxes:", detections['detection_boxes'][0].numpy()[:5])
print("Classes:", detections['detection_classes'][0].numpy().astype(np.int32)[:5])

cv2.imshow('Result', image_np)
cv2.waitKey(0)
cv2.destroyAllWindows()
