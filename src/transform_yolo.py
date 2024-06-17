import os
import pandas as pd
import ast
from PIL import Image
import shutil
import uuid

def load_csv(file_path):
    return pd.read_csv(file_path)

def parse_rectangles(rectangles_str):
    if pd.isna(rectangles_str):
        return []
    return ast.literal_eval(rectangles_str)

def convert_to_yolo_format(rect, img_width, img_height):
    x_center = (rect['xmin'] + rect['xmax']) / 2.0 / img_width
    y_center = (rect['ymin'] + rect['ymax']) / 2.0 / img_height
    width = (rect['xmax'] - rect['xmin']) / img_width
    height = (rect['ymax'] - rect['ymin']) / img_height
    return (x_center, y_center, width, height)

def main(input_csv, images_output_dir, labels_output_dir):
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)
    if not os.path.exists(labels_output_dir):
        os.makedirs(labels_output_dir)

    df = load_csv(input_csv)

    for index, row in df.iterrows():
        image_path = row['Png']
        rectangles = parse_rectangles(row['target'])
        
        if not os.path.exists(image_path):
            print(f"Image {image_path} does not exist, skipping.")
            continue

        image = Image.open(image_path)
        img_width, img_height = image.size

        # Generate a unique name for the image and corresponding label
        unique_name = str(uuid.uuid4())

        # Save the image to the YOLO images directory
        image.save(os.path.join(images_output_dir, f"{unique_name}.png"))

        # Prepare the label data in YOLO format
        yolo_labels = []
        for rect in rectangles:
            x_center, y_center, width, height = convert_to_yolo_format(rect, img_width, img_height)
            yolo_labels.append(f"0 {x_center} {y_center} {width} {height}")  # Assuming class_id is 0

        # Save the label to the YOLO labels directory
        with open(os.path.join(labels_output_dir, f"{unique_name}.txt"), 'w') as label_file:
            label_file.write("\n".join(yolo_labels))

if __name__ == "__main__":
    input_csv_path = '../datafile.csv'  # 输入CSV文件路径
    images_output_dir = '../yolo/images'  # 输出图片的目录
    labels_output_dir = '../yolo/labels'  # 输出标签的目录
    main(input_csv_path, images_output_dir, labels_output_dir)
