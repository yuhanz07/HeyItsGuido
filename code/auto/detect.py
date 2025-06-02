import cv2
import numpy as np
import tensorflow as tf
from picamera2 import Picamera2
from object_detection.utils import label_map_util, visualization_utils as viz_utils

# Paths
PATH_TO_MODEL = "/home/ndrobotics/code/Pi Only Files /4Pi/saved_model"
PATH_TO_LABELS = "/home/ndrobotics/code/Pi Only Files /4Pi/label_map.pbtxt"

# Load model and labels
detect_fn = tf.saved_model.load(PATH_TO_MODEL)
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

while True:
    frame = picam2.capture_array()

    input_tensor = tf.convert_to_tensor(frame)[tf.newaxis, ...]
    detections = detect_fn(input_tensor)

    viz_utils.visualize_boxes_and_labels_on_image_array(
        frame,
        detections['detection_boxes'][0].numpy(),
        detections['detection_classes'][0].numpy().astype(np.int32),
        detections['detection_scores'][0].numpy(),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=3,
        min_score_thresh=0.5
    )

    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()