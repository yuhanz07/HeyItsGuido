# import cv2
# import numpy as np
# import tensorflow as tf
# from picamera2 import Picamera2
# from object_detection.utils import label_map_util, visualization_utils as viz_utils
# from routine_move import routine_move
# 
# # Paths
# PATH_TO_MODEL = "/home/ndrobotics/code/tensorflow/saved_model"
# PATH_TO_LABELS = "/home/ndrobotics/code/tensorflow/label_map.pbtxt"
# 
# # Load model and labels
# detect_fn = tf.saved_model.load(PATH_TO_MODEL)
# category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)
# 
# # Initialize movement controller
# move = routine_move()
# 
# # Initialize camera
# picam2 = Picamera2()
# config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
# picam2.configure(config)
# picam2.start()
# 
# # Create a named window
# cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)
# 
# # Start moving forward
# move.move_forward(speed=50, duration=0.1)  # short pulse-based motion control
# 
# # Triangle similarity distance estimation constants
# KNOWN_HEIGHT = 0.12  # meters
# FOCAL_LENGTH = 850  # pixels (calibrate this based on your camera)
# 
# pending_action = None  # stores the next action to take
# best_left = {'score': 0, 'index': -1}
# best_right = {'score': 0, 'index': -1}
#         
# while True:
#     frame = picam2.capture_array()
#     input_tensor = tf.convert_to_tensor(frame)[tf.newaxis, ...]
#     detections = detect_fn(input_tensor)
# 
#     boxes = detections['detection_boxes'][0].numpy()
#     classes = detections['detection_classes'][0].numpy().astype(np.int32)
#     scores = detections['detection_scores'][0].numpy()
# 
#     viz_utils.visualize_boxes_and_labels_on_image_array(
#         frame, boxes, classes, scores, category_index,
#         use_normalized_coordinates=True,
#         line_thickness=3,
#         min_score_thresh=0.5
#     )
# 
#     yellow_detected = False
#     action_taken = False
# 
#     for i in range(len(scores)):
#         if scores[i] < 0.95:
#             continue
#         
#         class_id = classes[i]
#         class_name = category_index[class_id]['name']
#         
#         ymin, xmin, ymax, xmax = boxes[i]
#         bbox_width  = (xmax - xmin) * 640
#         bbox_height = (ymax - ymin) * 480
#         y_center    = (ymin + ymax) / 2
#         aspect_ratio = bbox_width / bbox_height if bbox_height != 0 else 0
# 
#         # FILTER OUT distant, tiny, or odd signs
#         if class_name in ['turnleft', 'turnright', 'stop', 'gostraight']:
#             if y_center < 0.4:
#                 print(f"{class_name} too high in frame (y_center={y_center:.2f}) ? skipping")
#                 continue
#             if bbox_width < 30 or bbox_height < 30:
#                 print(f"{class_name} too small (w={bbox_width:.0f}, h={bbox_height:.0f}) ? skipping")
#                 continue
#             if bbox_height > 300:
#                 print(f"{class_name} too large (h={bbox_height:.0f}) ? skipping")
#                 continue
#             if aspect_ratio < 0.3 or aspect_ratio > 3:
#                 print(f"{class_name} has odd shape (AR={aspect_ratio:.2f}) ? skipping")
#                 continue
# 
#         ymin, xmin, ymax, xmax = boxes[i]
#         bbox_height_pixels = (ymax - ymin) * 480
#         if bbox_height_pixels > 0:
#             distance = (KNOWN_HEIGHT * FOCAL_LENGTH) / bbox_height_pixels
#         else:
#             distance = float('inf')
# 
#         print(f"Detected {class_name} at ~{distance:.2f}m")
# 
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
# 
#     # Decide on left/right turn only if one is clearly more confident
#     if best_left['score'] > 0.95 and best_left['score'] - best_right['score'] > 0.1:
#         pending_action = 'turnleft'
#         action_taken = True
#         print("Committed to TURN LEFT (confident)")
#     elif best_right['score'] > 0.95 and best_right['score'] - best_left['score'] > 0.1:
#         pending_action = 'turnright'
#         action_taken = True
#         print("Committed to TURN RIGHT (confident)")
# 
# 
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
# 
#     cv2.imshow("Detection", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# 
# cv2.destroyAllWindows()
# picam2.stop()
# move.close()


# import cv2
# import numpy as np
# import tensorflow as tf
# from picamera2 import Picamera2
# from object_detection.utils import label_map_util, visualization_utils as viz_utils
# from routine_move import routine_move
# 
# # Paths
# PATH_TO_MODEL = "/home/ndrobotics/code/tensorflow/saved_model"
# PATH_TO_LABELS = "/home/ndrobotics/code/tensorflow/label_map.pbtxt"
# 
# # Load model and labels
# detect_fn = tf.saved_model.load(PATH_TO_MODEL)
# category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)
# 
# # Initialize movement controller
# move = routine_move()
# 
# # Initialize camera
# picam2 = Picamera2()
# config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
# picam2.configure(config)
# picam2.start()
# 
# # Create a named window
# cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)
# 
# # Start moving forward
# move.move_forward(speed=50, duration=0.1)  # short pulse-based motion control
# 
# # Triangle similarity distance estimation constants
# KNOWN_HEIGHT = 0.2  # meters
# FOCAL_LENGTH = 700  # pixels (calibrate this based on your camera)
# 
# pending_action = None  # stores the next action to take
# best_left = {'score': 0, 'index': -1}
# best_right = {'score': 0, 'index': -1}
#         
# while True:
#     frame = picam2.capture_array()
#     input_tensor = tf.convert_to_tensor(frame)[tf.newaxis, ...]
#     detections = detect_fn(input_tensor)
# 
#     boxes = detections['detection_boxes'][0].numpy()
#     classes = detections['detection_classes'][0].numpy().astype(np.int32)
#     scores = detections['detection_scores'][0].numpy()
# 
#     viz_utils.visualize_boxes_and_labels_on_image_array(
#         frame, boxes, classes, scores, category_index,
#         use_normalized_coordinates=True,
#         line_thickness=3,
#         min_score_thresh=0.5
#     )
# 
#     yellow_detected = False
#     action_taken = False
# 
#     for i in range(len(scores)):
#         if scores[i] < 0.95:
#             continue
#         
#         class_id = classes[i]
#         class_name = category_index[class_id]['name']
# 
#         ymin, xmin, ymax, xmax = boxes[i]
#         bbox_height_pixels = (ymax - ymin) * 480
#         if bbox_height_pixels > 0:
#             distance = (KNOWN_HEIGHT * FOCAL_LENGTH) / bbox_height_pixels
#         else:
#             distance = float('inf')
# 
#         print(f"Detected {class_name} at ~{distance:.2f}m")
# 
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
# 
#     # Decide on left/right turn only if one is clearly more confident
#     if best_left['score'] > 0.95 and best_left['score'] - best_right['score'] > 0.1:
#         pending_action = 'turnleft'
#         action_taken = True
#         print("Committed to TURN LEFT (confident)")
#     elif best_right['score'] > 0.95 and best_right['score'] - best_left['score'] > 0.1:
#         pending_action = 'turnright'
#         action_taken = True
#         print("Committed to TURN RIGHT (confident)")
# 
# 
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
# 
#     cv2.imshow("Detection", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# 
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

# Load model and labels
detect_fn = tf.saved_model.load(PATH_TO_MODEL)
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# Initialize movement controller
move = routine_move()

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# Create a named window
cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)

# Start moving forward
move.move_forward(speed=50, duration=0.1)  # short pulse-based motion control

# Triangle similarity distance estimation constants
KNOWN_HEIGHT = 0.2  # meters
FOCAL_LENGTH = 700  # pixels (calibrate this based on your camera)

pending_action = None  # stores the next action to take
best_left = {'score': 0, 'index': -1}
best_right = {'score': 0, 'index': -1}
        
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
        if scores[i] < 0.95:
            continue
        
        class_id = classes[i]
        class_name = category_index[class_id]['name']

        ymin, xmin, ymax, xmax = boxes[i]
        bbox_height_pixels = (ymax - ymin) * 480
        if bbox_height_pixels > 0:
            distance = (KNOWN_HEIGHT * FOCAL_LENGTH) / bbox_height_pixels
        else:
            distance = float('inf')

        print(f"Detected {class_name} at ~{distance:.2f}m")

        if class_name == 'yellowline':
            yellow_detected = True
        elif class_name == 'stop' and distance < 0.7:
            pending_action = 'stop'
            action_taken = True
        elif class_name == 'gostraight' and distance < 1.0:
            move.move_forward(speed=50, duration=1.25)
            action_taken = True
        elif class_name == 'turnleft' and distance < 0.7:
            if scores[i] > best_left['score']:
                best_left = {'score': scores[i], 'index': i, 'distance': distance}
        elif class_name == 'turnright' and distance < 0.7:
            if scores[i] > best_right['score']:
                best_right = {'score': scores[i], 'index': i, 'distance': distance}

    # Decide on left/right turn only if one is clearly more confident
    if best_left['score'] > 0.95 and best_left['score'] - best_right['score'] > 0.1:
        pending_action = 'turnleft'
        action_taken = True
        print("Committed to TURN LEFT (confident)")
    elif best_right['score'] > 0.95 and best_right['score'] - best_left['score'] > 0.1:
        pending_action = 'turnright'
        action_taken = True
        print("Committed to TURN RIGHT (confident)")


    # Execute pending action (if any)
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
        pending_action = None  # clear it after action
    elif not action_taken:
        # Normal behavior: follow yellow line or stop
        if yellow_detected:
            move.move_forward(speed=50, duration=0.5)
        else:
            move.stop(duration=0.2)  # safety stop

    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
move.close()



import cv2
import numpy as np
import tensorflow as tf
from picamera2 import Picamera2
from object_detection.utils import label_map_util, visualization_utils as viz_utils
from routine_move import routine_move

# Paths
PATH_TO_MODEL = "/home/ndrobotics/code/tensorflow/saved_model"
PATH_TO_LABELS = "/home/ndrobotics/code/tensorflow/label_map.pbtxt"

# Load model and labels
detect_fn = tf.saved_model.load(PATH_TO_MODEL)
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS)

# Initialize movement controller
move = routine_move()

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# Create a named window
cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)

# Start moving forward
move.move_forward(speed=50, duration=0.1)  # short pulse-based motion control

# Triangle similarity distance estimation constants
KNOWN_HEIGHT = 0.2  # meters
FOCAL_LENGTH = 700  # pixels (calibrate this based on your camera)

pending_action = None  # stores the next action to take
best_left = {'score': 0, 'index': -1}
best_right = {'score': 0, 'index': -1}
        
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
        if scores[i] < 0.95:
            continue
        
        class_id = classes[i]
        class_name = category_index[class_id]['name']

        ymin, xmin, ymax, xmax = boxes[i]
        bbox_height_pixels = (ymax - ymin) * 480
        if bbox_height_pixels > 0:
            distance = (KNOWN_HEIGHT * FOCAL_LENGTH) / bbox_height_pixels
        else:
            distance = float('inf')

        print(f"Detected {class_name} at ~{distance:.2f}m")

        if class_name == 'yellowline':
            yellow_detected = True
        elif class_name == 'stop' and distance < 0.7:
            pending_action = 'stop'
            action_taken = True
        elif class_name == 'gostraight' and distance < 1.0:
            move.move_forward(speed=50, duration=1.25)
            action_taken = True
        elif class_name == 'turnleft' and distance < 0.7:
            if scores[i] > best_left['score']:
                best_left = {'score': scores[i], 'index': i, 'distance': distance}
        elif class_name == 'turnright' and distance < 0.7:
            if scores[i] > best_right['score']:
                best_right = {'score': scores[i], 'index': i, 'distance': distance}

    # Decide on left/right turn only if one is clearly more confident
    if best_left['score'] > 0.95 and best_left['score'] - best_right['score'] > 0.1:
        pending_action = 'turnleft'
        action_taken = True
        print("Committed to TURN LEFT (confident)")
    elif best_right['score'] > 0.95 and best_right['score'] - best_left['score'] > 0.1:
        pending_action = 'turnright'
        action_taken = True
        print("Committed to TURN RIGHT (confident)")


    # Execute pending action (if any)
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
        pending_action = None  # clear it after action
    elif not action_taken:
        # Normal behavior: follow yellow line or stop
        if yellow_detected:
            move.move_forward(speed=50, duration=0.5)
        else:
            move.stop(duration=0.2)  # safety stop

    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
move.close()















