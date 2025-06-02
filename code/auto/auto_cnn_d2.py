import cv2
import numpy as np
import tensorflow as tf
import time
from picamera2 import Picamera2
from object_detection.utils import label_map_util, visualization_utils as viz_utils
from routine_move import routine_move

def auto_cnn_d():
    # Paths
    PATH_TO_MODEL = "/home/ndrobotics/code/tensorflow/saved_model"
    PATH_TO_LABELS = "/home/ndrobotics/code/tensorflow/label_map.pbtxt"
    PATH_TO_CNN_MODEL = "/home/ndrobotics/code/tensorflow/models/research/turn_classifier.h5"

    # Load models
    detect_fn = tf.saved_model.load(PATH_TO_MODEL)
    cnn_model = tf.keras.models.load_model(PATH_TO_CNN_MODEL)
    class_names = ['turnleft', 'turnright']
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
    ACTION_COOLDOWN = 3.0  # seconds
    action_lock_until = 0
    pending_action = None
    recent_preds = []  # for majority voting

    while True:
        frame = picam2.capture_array()
        if frame is None:
            continue

        current_time = time.time()
        yellow_detected = False
        action_taken = False

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

        if current_time >= action_lock_until:
            for i in range(len(scores)):
                if scores[i] < 0.95:
                    continue

                class_id = classes[i]
                class_name = category_index[class_id]['name']
                ymin, xmin, ymax, xmax = boxes[i]

                (h, w) = frame.shape[:2]
                x1 = max(0, int(xmin * w))
                y1 = max(0, int(ymin * h))
                x2 = min(w, int(xmax * w))
                y2 = min(h, int(ymax * h))

                box_h = (ymax - ymin) * h
                distance = (KNOWN_HEIGHT * FOCAL_LENGTH) / box_h if box_h > 0 else float('inf')

                pad_x = int((x2 - x1) * 0.2)
                pad_y = int((y2 - y1) * 0.2)
                x1 = max(0, x1 - pad_x)
                y1 = max(0, y1 - pad_y)
                x2 = min(w, x2 + pad_x)
                y2 = min(h, y2 + pad_y)

                roi = frame[y1:y2, x1:x2]
                if roi.size == 0:
                    continue

                try:
                    cnn_img = cv2.resize(roi, (64, 64))
                    cnn_img = cv2.cvtColor(cnn_img, cv2.COLOR_BGR2RGB)
                    cnn_img = cnn_img.astype("float32") / 255.0
                    cnn_img = np.expand_dims(cnn_img, axis=0)

                    pred = cnn_model.predict(cnn_img)
                    label_index = np.argmax(pred[0])
                    confidence = pred[0][label_index]
                    label = class_names[label_index]

                    print(f"[CNN] Prediction: {label} ({confidence:.2f}) at distance {distance:.2f}m")

                    if label in ['turnleft', 'turnright'] and confidence > 0.90 and distance < 0.7:
                        recent_preds.append(label)

                        if len(recent_preds) >= 3:
                            final_decision = max(set(recent_preds), key=recent_preds.count)
                            print(f"[CNN] Final decision after voting: {final_decision}")
                            pending_action = final_decision
                            action_taken = True
                            recent_preds.clear()
                            break
                except Exception as e:
                    print("CNN error:", e)

        if pending_action and current_time >= action_lock_until:
            print(f"Executing action: {pending_action}")
            if pending_action == 'turnleft':
                move.move_forward(speed=50, duration=2.75)
                move.turn_left(speed=30, duration=1.75)
            elif pending_action == 'turnright':
                move.move_forward(speed=50, duration=2.68)
                move.turn_right(speed=30, duration=2.0)
            action_lock_until = time.time() + ACTION_COOLDOWN
            pending_action = None
            action_taken = True

        if not action_taken and current_time >= action_lock_until:
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
                    break
                elif class_name == 'gostraight':
                    move.move_forward(speed=50, duration=1.25)
                    action_taken = True
                    break

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


