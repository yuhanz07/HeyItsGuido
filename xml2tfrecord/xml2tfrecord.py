import os
import io
import pandas as pd
import tensorflow as tf
import xml.etree.ElementTree as ET
from PIL import Image
from object_detection.utils import dataset_util

# --- USER CONFIG ---
LABEL_MAP = {'gostraight': 1, 'turnleft': 2}  # must match label_map.pbtxt
IMAGE_DIR = "/Users/wanhoo/Documents/CSE40883/code/Pi Only Files/captured_pic"
ANNOTATION_DIR = "/Users/wanhoo/Documents/CSE40883/code/Pi Only Files/captured_pic"
SPLIT = "train"  # or "val"
SPLIT_LIST = "/Users/wanhoo/Documents/CSE40883/code/xml2tfrecord/train.txt"  # a txt file listing filenames (no extension) to include in this TFRecord
OUTPUT_PATH = f"/Users/wanhoo/Documents/CSE40883/code/xml2tfrecord/{SPLIT}.record"

# --- CORE LOGIC ---
def create_tf_example(xml_path, image_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    with tf.io.gfile.GFile(image_path, 'rb') as fid:
        encoded_image = fid.read()
    image = Image.open(io.BytesIO(encoded_image))
    width, height = image.size

    filename = os.path.basename(image_path).encode('utf8')
    image_format = b'jpg'

    xmins, xmaxs, ymins, ymaxs, classes_text, classes = [], [], [], [], [], []

    for member in root.findall('object'):
        cls = member[0].text
        if cls not in LABEL_MAP:
            continue

        bndbox = member.find('bndbox')
        xmins.append(float(bndbox.find('xmin').text) / width)
        xmaxs.append(float(bndbox.find('xmax').text) / width)
        ymins.append(float(bndbox.find('ymin').text) / height)
        ymaxs.append(float(bndbox.find('ymax').text) / height)
        classes_text.append(cls.encode('utf8'))
        classes.append(LABEL_MAP[cls])

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_image),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def main():
    writer = tf.io.TFRecordWriter(OUTPUT_PATH)

    with open(SPLIT_LIST, 'r') as f:
        file_ids = [line.strip() for line in f.readlines() if line.strip()]

    for file_id in file_ids:
        xml_path = os.path.join(ANNOTATION_DIR, file_id + ".xml")
        image_path = os.path.join(IMAGE_DIR, file_id + ".jpg")
        if not os.path.exists(xml_path) or not os.path.exists(image_path):
            continue
        tf_example = create_tf_example(xml_path, image_path)
        writer.write(tf_example.SerializeToString())

    writer.close()
    print(f"Wrote TFRecord to {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
