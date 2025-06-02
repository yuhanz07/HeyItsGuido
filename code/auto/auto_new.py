# import cv2
# import numpy as np
# import tensorflow as tf
# from picamera2 import Picamera2
# from object_detection.utils import label_map_util, visualization_utils as viz_utils
# from routine_move import routine_move

# # Paths
# PATH_TO_MODEL = "/home/ndrobotics/code/Pi Only Files /4Pi/saved_model"
# PATH_TO_LABELS = "/home/ndrobotics/code/Pi Only Files /4Pi/label_map.pbtxt"

# # Load model and labels
# detect_fn = tf.saved_model.load(PATH_TO_MODEL)
# category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# # Initialize movement controller
# move = routine_move()

# # Initialize camera
# picam2 = Picamera2()
# config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
# picam2.configure(config)
# picam2.start()

# # Create a named window
# cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)

# while True:
#     frame = picam2.capture_array()

#     input_tensor = tf.convert_to_tensor(frame)[tf.newaxis, ...]
#     detections = detect_fn(input_tensor)

#     # Extract detection classes and scores
#     detection_classes = detections['detection_classes'][0].numpy().astype(np.int32)
#     detection_scores = detections['detection_scores'][0].numpy()

#     # Visualize detections
#     viz_utils.visualize_boxes_and_labels_on_image_array(
#         frame,
#         detections['detection_boxes'][0].numpy(),
#         detection_classes,
#         detection_scores,
#         category_index,
#         use_normalized_coordinates=True,
#         line_thickness=3,
#         min_score_thresh=0.5
#     )

#     # Display the resulting frame
#     cv2.imshow("Detection", frame)

#     # Check for specific detections and perform actions
#     for i in range(len(detection_scores)):
#         score = detection_scores[i]
#         if score > 0.9:
#             class_id = detection_classes[i]
#             class_name = category_index[class_id]['name']
#             print(f"Detected object: {class_name} with confidence {score:.2f}")

#             if class_name == 'stop': ## big changes here
#                 move.stop(duration=0.5)
#             elif class_name == 'turnleft':
#                 move.turn_left(speed=30, duration=1)
#             elif class_name == 'turnright':
#                 move.turn_right(speed=30, duration=1)
#             elif class_name == 'gostraight':
#                 move.move_forward(speed=50, duration=2)

#     # Press 'q' to exit
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release resources
# cv2.destroyAllWindows()
# picam2.stop()
# move.close()


# import cv2
# import numpy as np
# import tensorflow as tf
# from picamera2 import Picamera2
# from object_detection.utils import label_map_util, visualization_utils as viz_utils
# from routine_move import routine_move

# # Paths
# PATH_TO_MODEL = "/home/ndrobotics/code/tensorflow/saved_model"
# PATH_TO_LABELS = "/home/ndrobotics/code/tensorflow/label_map.pbtxt"

# # Load model and labels
# detect_fn = tf.saved_model.load(PATH_TO_MODEL)
# category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# # Initialize movement controller
# move = routine_move()

# # Initialize camera
# picam2 = Picamera2()
# config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
# picam2.configure(config)
# picam2.start()

# # Create a named window
# cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)

# # Start moving forward
# move.move_forward(speed=50, duration=0.1)  # short pulse-based motion control

# # Triangle similarity distance estimation constants
# KNOWN_HEIGHT = 0.2  # meters
# FOCAL_LENGTH = 700  # pixels (calibrate this based on your camera)

# pending_action = None  # stores the next action to take
# best_left = {'score': 0, 'index': -1}
# best_right = {'score': 0, 'index': -1}
        
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

#     for i in range(len(scores)):
#         if scores[i] < 0.95:
#             continue
        
#         class_id = classes[i]
#         class_name = category_index[class_id]['name']

#         ymin, xmin, ymax, xmax = boxes[i]
#         bbox_height_pixels = (ymax - ymin) * 480
#         if bbox_height_pixels > 0:
#             distance = (KNOWN_HEIGHT * FOCAL_LENGTH) / bbox_height_pixels
#         else:
#             distance = float('inf')

#         print(f"Detected {class_name} at ~{distance:.2f}m")

#         if class_name == 'yellowline':
#             yellow_detected = True
#         elif class_name == 'stop' and distance < 0.7:
#             pending_action = 'stop'
#             action_taken = True
#         elif class_name == 'gostraight' and distance < 1.0:
#             move.move_forward(speed=50, duration=1.25)
#             action_taken = True
#         elif class_name == 'turnleft' and distance < 0.7:
#             if scores[i] > best_left['score']:
#                 best_left = {'score': scores[i], 'index': i, 'distance': distance}
#         elif class_name == 'turnright' and distance < 0.7:
#             if scores[i] > best_right['score']:
#                 best_right = {'score': scores[i], 'index': i, 'distance': distance}

#     # Decide on left/right turn only if one is clearly more confident
#     if best_left['score'] > 0.95 and best_left['score'] - best_right['score'] > 0.1:
#         pending_action = 'turnleft'
#         action_taken = True
#         print("Committed to TURN LEFT (confident)")
#     elif best_right['score'] > 0.95 and best_right['score'] - best_left['score'] > 0.1:
#         pending_action = 'turnright'
#         action_taken = True
#         print("Committed to TURN RIGHT (confident)")


#     # Execute pending action (if any)
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
#         pending_action = None  # clear it after action
#     elif not action_taken:
#         # Normal behavior: follow yellow line or stop
#         if yellow_detected:
#             move.move_forward(speed=50, duration=0.5)
#         else:
#             move.stop(duration=0.2)  # safety stop

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
class_names = ['turnleft', 'turnright']  # must match your CNN training order
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# Movement controller
move = routine_move()

# Camera setup
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)

# Triangle similarity constants
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
    turn_roi = None

    for i in range(len(scores)):
        if scores[i] < 0.85:
            continue

        class_id = classes[i]
        class_name = category_index[class_id]['name']

        ymin, xmin, ymax, xmax = boxes[i]
        bbox_height_pixels = (ymax - ymin) * 480
        distance = (KNOWN_HEIGHT * FOCAL_LENGTH) / bbox_height_pixels if bbox_height_pixels > 0 else float('inf')

        print(f"Detected {class_name} at ~{distance:.2f}m")

        if class_name == 'yellowline':
            yellow_detected = True
        elif class_name == 'stop' and distance < 0.7:
            pending_action = 'stop'
            action_taken = True
        elif class_name == 'gostraight' and distance < 1.0:
            move.move_forward(speed=50, duration=1.25)
            action_taken = True
        elif class_name in ['turnleft', 'turnright'] and distance < 0.7:
            (h, w) = frame.shape[:2]
            (startY, startX, endY, endX) = (int(ymin * h), int(xmin * w), int(ymax * h), int(xmax * w))
            turn_roi = frame[startY:endY, startX:endX]

    if turn_roi is not None and not action_taken:
        try:
            # Original box
            ymin, xmin, ymax, xmax = boxes[best['index']]
            (x1, y1, x2, y2) = int(xmin * width), int(ymin * height), int(xmax * width), int(ymax * height)

            # Padding factor (e.g. 20% of width/height)
            pad_x = int((x2 - x1) * 0.2)
            pad_y = int((y2 - y1) * 0.2)

            # Expand bounds, ensuring we stay within image
            x1 = max(0, x1 - pad_x)
            y1 = max(0, y1 - pad_y)
            x2 = min(width, x2 + pad_x)
            y2 = min(height, y2 + pad_y)

            turn_roi = frame[y1:y2, x1:x2]
            cv2.imwrite("turn_roi.jpg", turn_roi)
            
            cnn_img = cv2.resize(turn_roi, (64, 64))
            cnn_img = cnn_img.astype("float32") / 255.0
            cnn_img = np.expand_dims(cnn_img, axis=0)
            pred = cnn_model.predict(cnn_img)
            label = class_names[np.argmax(pred[0])]
            print("CNN classified as:", label)

            if label == "turnleft":
                pending_action = 'turnleft'
                action_taken = True
            elif label == "turnright":
                pending_action = 'turnright'
                action_taken = True
        except Exception as e:
            print("Error in CNN classification:", e)

    if pending_action:
        print(f"Executing pending action: {pending_action}")
        if pending_action == 'stop':
            move.move_forward(speed=50, duration=1.2)
            move.stop(duration=1)
        elif pending_action == 'turnleft':
            move.move_forward(speed=50, duration=1.1)
            move.turn_left(speed=30, duration=1.45)
        elif pending_action == 'turnright':
            move.move_forward(speed=50, duration=1.1)
            move.turn_right(speed=30, duration=1.45)
        pending_action = None
    elif not action_taken:
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

