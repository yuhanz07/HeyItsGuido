# import os
# import imageio
# import numpy as np
# from imgaug import augmenters as iaa
# from PIL import Image

# # Set paths
# input_folder = 'input_images/'
# output_folder = 'augmented_images/'
# os.makedirs(output_folder, exist_ok=True)

# # Define augmentations
# seq = iaa.Sequential([
#     iaa.Fliplr(0.5),  # horizontal flip
#     iaa.Affine(rotate=(-25, 25)),  # rotation
#     iaa.Multiply((0.7, 1.3)),  # brightness
#     iaa.AdditiveGaussianNoise(scale=(5, 15)),  # noise
#     iaa.GaussianBlur(sigma=(0.0, 1.0))  # blur
# ])

# # Load all images
# images = [imageio.imread(os.path.join(input_folder, img)) for img in os.listdir(input_folder)]

# # Generate 500 augmented images
# count = 0
# while count < 500:
#     batch = seq(images=np.array(images))
#     for img in batch:
#         img_pil = Image.fromarray(img)
#         img_pil.save(os.path.join(output_folder, f"aug_{count}.jpg"))
#         count += 1
#         if count >= 500:
#             break



import os
import xml.etree.ElementTree as ET
import numpy as np
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
import imageio.v2 as imageio
from PIL import Image
import shutil

input_img_dir = '/Users/wanhoo/Documents/CSE40883/dataset/captured_pic'
input_xml_dir = '/Users/wanhoo/Documents/CSE40883/dataset/captured_pic'
output_img_dir = '/Users/wanhoo/Documents/CSE40883/dataset/newcappic'
output_xml_dir = '/Users/wanhoo/Documents/CSE40883/dataset/newcappic'

os.makedirs(output_img_dir, exist_ok=True)
os.makedirs(output_xml_dir, exist_ok=True)

# Define augmentations (these affect both image & bounding box)
seq = iaa.Sequential([
    iaa.Fliplr(0.5),
    iaa.Affine(rotate=(-25, 25)),
    iaa.Multiply((0.7, 1.3)),
    iaa.AdditiveGaussianNoise(scale=(5, 15)),
    iaa.GaussianBlur(sigma=(0.0, 1.0))
])

def parse_voc_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    bboxes = []
    for obj in root.findall('object'):
        name = obj.find('name').text
        xml_box = obj.find('bndbox')
        bbox = BoundingBox(
            x1=int(xml_box.find('xmin').text),
            y1=int(xml_box.find('ymin').text),
            x2=int(xml_box.find('xmax').text),
            y2=int(xml_box.find('ymax').text),
            label=name
        )
        bboxes.append(bbox)
    return tree, root, bboxes

def update_voc_xml(root, bboxes_aug, new_filename, img_shape):
    # Update filename and size
    root.find('filename').text = new_filename
    size = root.find('size')
    size.find('width').text = str(img_shape[1])
    size.find('height').text = str(img_shape[0])

    # Remove old objects
    for obj in root.findall('object'):
        root.remove(obj)

    for bbox in bboxes_aug.bounding_boxes:
        obj = ET.SubElement(root, 'object')
        ET.SubElement(obj, 'name').text = bbox.label
        ET.SubElement(obj, 'pose').text = 'Unspecified'
        ET.SubElement(obj, 'truncated').text = '0'
        ET.SubElement(obj, 'difficult').text = '0'
        bndbox = ET.SubElement(obj, 'bndbox')
        ET.SubElement(bndbox, 'xmin').text = str(int(bbox.x1))
        ET.SubElement(bndbox, 'ymin').text = str(int(bbox.y1))
        ET.SubElement(bndbox, 'xmax').text = str(int(bbox.x2))
        ET.SubElement(bndbox, 'ymax').text = str(int(bbox.y2))
    return root

original_files = [f for f in os.listdir(input_img_dir) if f.lower().endswith(('.jpg', '.png'))]
image_count = 0

while image_count < 500:
    for img_file in original_files:
        img_path = os.path.join(input_img_dir, img_file)
        xml_path = os.path.join(input_xml_dir, os.path.splitext(img_file)[0] + '.xml')

        image = imageio.imread(img_path)
        tree, root, bboxes = parse_voc_xml(xml_path)
        bbs_on_image = BoundingBoxesOnImage(bboxes, shape=image.shape)

        image_aug, bbs_aug = seq(image=image, bounding_boxes=bbs_on_image)
        bbs_aug = bbs_aug.remove_out_of_image().clip_out_of_image()

        # Save augmented image
        new_img_name = f"aug_{image_count}.jpg"
        Image.fromarray(image_aug).save(os.path.join(output_img_dir, new_img_name))

        # Save updated XML
        new_xml_root = update_voc_xml(root, bbs_aug, new_img_name, image_aug.shape)
        tree.write(os.path.join(output_xml_dir, f"aug_{image_count}.xml"))
        
        image_count += 1
        if image_count >= 500:
            break

