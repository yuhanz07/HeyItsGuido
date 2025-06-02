# import cv2
# import numpy as np
# import tensorflow as tf
# from picamera2 import Picamera2
# from object_detection.utils import label_map_util, visualization_utils as viz_utils
# from routine_move import routine_move

# # Paths
# PATH_TO_MODEL = "/home/ndrobotics/code/tensorflow/saved_model"
# PATH_TO_LABELS = "/home/ndrobotics/code/tensorflow/label_map.pbtxt"
# PATH_TO_CNN_MODEL = "/home/ndrobotics/code/tensorflow/models/research/turn_classifier.h5"

# # Load models
# detect_fn = tf.saved_model.load(PATH_TO_MODEL)
# cnn_model = tf.keras.models.load_model(PATH_TO_CNN_MODEL)
# class_names = ['turnleft', 'turnright']
# category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# # Movement controller
# move = routine_move()

# # Camera setup
# picam2 = Picamera2()
# config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
# picam2.configure(config)
# picam2.start()

# cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)

# # Triangle similarity constants
# KNOWN_HEIGHT = 0.2  # meters
# FOCAL_LENGTH = 700

# pending_action = None

# while True:
#     frame = picam2.capture_array()
#     input_tensor = tf.convert_to_tensor(frame)[tf.newaxis, ...]
#     detections = detect_fn(input_tensor)

#     boxes = detections['detection_boxes'][0].numpy()
#     classes = detections['detection_classes'][0].numpy().astype(np.int32)
#     scores = detections['detection_scores'][0].numpy()

#     viz_utils.visualize_boxes_and_labels_on_image_array(
#         frame, boxes, classes, scores, category_index,
#         use_normalized_coordinates=True,
#         line_thickness=3,
#         min_score_thresh=0.5
#     )

#     yellow_detected = False
#     action_taken = False
#     turn_roi = None
#     turn_label = None

#     for i in range(len(scores)):
#         if scores[i] < 0.95:
#             continue

#         class_id = classes[i]
#         class_name = category_index[class_id]['name']

#         ymin, xmin, ymax, xmax = boxes[i]
#         bbox_height_pixels = (ymax - ymin) * 480
#         distance = (KNOWN_HEIGHT * FOCAL_LENGTH) / bbox_height_pixels if bbox_height_pixels > 0 else float('inf')

#         print(f"Detected {class_name} at ~{distance:.2f}m")

#         if class_name == 'yellowline':
#             yellow_detected = True
#         elif class_name == 'stop' and distance < 0.7:
#             pending_action = 'stop'
#             action_taken = True
#         elif class_name == 'gostraight' and distance < 1.0:
#             move.move_forward(speed=50, duration=1.25)
#             action_taken = True
#         elif class_name in ['turnleft', 'turnright'] and distance < 0.7:
#             (h, w) = frame.shape[:2]
#             x1 = int(xmin * w)
#             y1 = int(ymin * h)
#             x2 = int(xmax * w)
#             y2 = int(ymax * h)

#             # Expand bounds by 20%
#             pad_x = int((x2 - x1) * 0.2)
#             pad_y = int((y2 - y1) * 0.2)
#             x1 = max(0, x1 - pad_x)
#             y1 = max(0, y1 - pad_y)
#             x2 = min(w, x2 + pad_x)
#             y2 = min(h, y2 + pad_y)

#             turn_roi = frame[y1:y2, x1:x2]
#             turn_label = class_name
#             break  # use the first valid ROI only

#     # Skip detection label, always use CNN to decide direction
#     if turn_roi is not None and not action_taken:
#         try:
#             cnn_img = cv2.resize(turn_roi, (64, 64))
#             cnn_img = cv2.cvtColor(cnn_img, cv2.COLOR_BGR2RGB)
#             cnn_img = cnn_img.astype("float32") / 255.0
#             cnn_img = np.expand_dims(cnn_img, axis=0)
#             pred = cnn_model.predict(cnn_img)
#             label_index = np.argmax(pred[0])
#             label_confidence = np.max(pred[0])
#             label = class_names[label_index]

#             print(f"[CNN] Prediction: {label} ({label_confidence:.2f})")

#             if label_confidence > 0.85:
#                 pending_action = label
#                 action_taken = True

#         except Exception as e:
#             print("Error in CNN classification:", e)

#     if pending_action:
#         print(f"Executing pending action: {pending_action}")
#         if pending_action == 'stop':
#             move.move_forward(speed=50, duration=1.2)
#             move.stop(duration=1)
#         elif pending_action == 'turnleft':
#             move.move_forward(speed=50, duration=1.1)
#             move.turn_left(speed=30, duration=1.45)
#         elif pending_action == 'turnright':
#             move.move_forward(speed=50, duration=1.1)
#             move.turn_right(speed=30, duration=1.45)
#         pending_action = None

#     elif not action_taken:
#         if yellow_detected:
#             move.move_forward(speed=50, duration=0.5)
#         else:
#             move.stop(duration=0.2)

#     cv2.imshow("Detection", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cv2.destroyAllWindows()
# picam2.stop()
# move.close()


import cv2
import numpy as np
import tensorflow as tf
from picamera2 import Picamera2
from object_detection.utils import label_map_util, visualization_utils as viz_utils
from routine_move import routine_move

# Paths
PATH_TO_MODEL = "/home/ndrobotics/code/tensorflow/saved_model"
PATH_TO_LABELS = "/home/ndrobotics/code/tensorflow/label_map.pbtxt"
PATH_TO_CNN_MODEL = "/home/ndrobotics/code/tensorflow/models/research/turn_classifier.h5"

# Load models
detect_fn = tf.saved_model.load(PATH_TO_MODEL)
cnn_model = tf.keras.models.load_model(PATH_TO_CNN_MODEL)
class_names = ['turnleft', 'turnright']  # should match CNN training
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# Movement controller
move = routine_move()

# Camera setup
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)

# Constants
KNOWN_HEIGHT = 0.2  # meters
FOCAL_LENGTH = 700

pending_action = None

while True:
    frame = picam2.capture_array()
    input_tensor = tf.convert_to_tensor(frame)[tf.newaxis, ...]
    detections = detect_fn(input_tensor)

    boxes = detections['detection_boxes'][0].numpy()
    classes = detections['detection_classes'][0].numpy().astype(np.int32)
    scores = detections['detection_scores'][0].numpy()

    viz_utils.visualize_boxes_and_labels_on_image_array(
        frame, boxes, classes, scores, category_index,
        use_normalized_coordinates=True,
        line_thickness=3,
        min_score_thresh=0.5
    )

    yellow_detected = False
    action_taken = False

    for i in range(len(scores)):
        if scores[i] < 0.5:
            continue

        ymin, xmin, ymax, xmax = boxes[i]
        (h, w) = frame.shape[:2]
        (startY, startX, endY, endX) = (int(ymin * h), int(xmin * w), int(ymax * h), int(xmax * w))
        if endY - startY <= 0 or endX - startX <= 0:
            continue
        
        box_h = endY - startY
        box_w = endX - startX
        pad_h = int(box_h * 0.2)
        pad_w = int(box_w * 0.2)
        startY = max(0, startY - pad_h)
        endY = min(h, endY + pad_h)
        startX = max(0, startX - pad_w)
        endX = min(w, endX + pad_w)

        roi = frame[startY:endY, startX:endX]
        if roi.size == 0:
            continue

        try:
            cnn_img = cv2.resize(roi, (64, 64))
            cnn_img = cnn_img.astype("float32") / 255.0
            cnn_img = np.expand_dims(cnn_img, axis=0)
            pred = cnn_model.predict(cnn_img)
            label_index = np.argmax(pred[0])
            confidence = pred[0][label_index]
            label = class_names[label_index]

            print(f"[CNN] Prediction: {label} ({confidence:.2f})")

            if label in ['turnleft', 'turnright'] and confidence > 0.90:
                pending_action = label
                action_taken = True
                break

        except Exception as e:
            print("CNN error:", e)

    if pending_action:
        print(f"Executing action: {pending_action}")
        if pending_action == 'turnleft':
            move.move_forward(speed=50, duration=2.75)
            move.turn_left(speed=30, duration=1.75)
        elif pending_action == 'turnright':
            move.move_forward(speed=50, duration=2.68)
            move.turn_right(speed=30, duration=2)
        pending_action = None

    elif not action_taken:
        for i in range(len(scores)):
            if scores[i] < 0.90:
                continue
            class_id = classes[i]
            class_name = category_index[class_id]['name']
            if class_name == 'yellowline':
                yellow_detected = True
            elif class_name == 'stop':
                move.stop(duration=1.2)
                action_taken = True
            elif class_name == 'gostraight':
                move.move_forward(speed=50, duration=1.25)
                action_taken = True

        if not action_taken:
            if yellow_detected:
                move.move_forward(speed=50, duration=0.5)
            else:
                move.stop(duration=0.2)

    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
move.close()
