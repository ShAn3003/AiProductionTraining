import os
import random
import shutil
from PIL import Image, ImageOps
from tqdm import tqdm

# 原始数据集路径
data_dir = "../yolo"
images_dir = os.path.join(data_dir, "images")
labels_dir = os.path.join(data_dir, "labels")

# 临时增强数据集路径
aug_images_dir = os.path.join(data_dir, "augmented_images")
aug_labels_dir = os.path.join(data_dir, "augmented_labels")

# 分割后的数据集路径
train_dir = "../augmented_yolo/train"
val_dir = "../augmented_yolo/validation"
test_dir = "../augmented_yolo/test"

# 创建目标文件夹
os.makedirs(aug_images_dir, exist_ok=True)
os.makedirs(aug_labels_dir, exist_ok=True)
os.makedirs(os.path.join(train_dir, "images"), exist_ok=True)
os.makedirs(os.path.join(train_dir, "labels"), exist_ok=True)
os.makedirs(os.path.join(val_dir, "images"), exist_ok=True)
os.makedirs(os.path.join(val_dir, "labels"), exist_ok=True)
os.makedirs(os.path.join(test_dir, "images"), exist_ok=True)
os.makedirs(os.path.join(test_dir, "labels"), exist_ok=True)

# 获取所有图片文件名
image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]

# 数据增强操作
def augment_image_and_labels(image, labels):
    augmented_images = [image]  # 保留原始图像
    augmented_labels = [labels]
    
    # 添加翻转
    augmented_images.append(ImageOps.mirror(image))
    augmented_labels.append(adjust_labels_for_mirror(labels))

    augmented_images.append(ImageOps.flip(image))
    augmented_labels.append(adjust_labels_for_flip(labels))

    # 添加旋转
    for angle in [90, 180, 270]:
        rotated_image = image.rotate(angle, expand=True)
        augmented_images.append(rotated_image)
        augmented_labels.append(adjust_labels_for_rotation(labels, angle, image.size, rotated_image.size))

    return augmented_images, augmented_labels

def adjust_labels_for_mirror(labels):
    new_labels = []
    for label in labels:
        class_id, cx, cy, w, h = map(float, label.split())
        cx = 1 - cx  # 水平翻转X坐标
        new_labels.append(f"{class_id} {cx} {cy} {w} {h}\n")
    return new_labels

def adjust_labels_for_flip(labels):
    new_labels = []
    for label in labels:
        class_id, cx, cy, w, h = map(float, label.split())
        cy = 1 - cy  # 垂直翻转Y坐标
        new_labels.append(f"{class_id} {cx} {cy} {w} {h}\n")
    return new_labels

def adjust_labels_for_rotation(labels, angle, original_size, new_size):
    new_labels = []
    w_ori, h_ori = original_size
    w_new, h_new = new_size
    for label in labels:
        class_id, cx, cy, w, h = map(float, label.split())
        if angle == 90:
            new_cx = cy
            new_cy = 1 - cx
            new_w = h * h_new / h_ori
            new_h = w * w_new / w_ori
        elif angle == 180:
            new_cx = 1 - cx
            new_cy = 1 - cy
            new_w = w
            new_h = h
        elif angle == 270:
            new_cx = 1 - cy
            new_cy = cx
            new_w = h * h_new / h_ori
            new_h = w * w_new / w_ori
        new_labels.append(f"{class_id} {new_cx} {new_cy} {new_w} {new_h}\n")
    return new_labels

# 增强数据并保存到临时目录
augmented_images = []
no_target_images = []

for img_file in tqdm(image_files, desc="Processing images"):
    img_path = os.path.join(images_dir, img_file)
    txt_path = os.path.join(labels_dir, img_file.replace('.jpg', '.txt'))
    
    try:
        with open(txt_path, 'r') as file:
            lines = file.readlines()
        
        if lines:
            image = Image.open(img_path).convert("L")  # 确保是灰度图像
            augmented_imgs, augmented_lbls = augment_image_and_labels(image, lines)
            for i, (aug_img, aug_lbl) in enumerate(zip(augmented_imgs, augmented_lbls)):
                #aug_img_file保存的是对应增强文件的文件名
                aug_img_file = f"{os.path.splitext(img_file)[0]}_aug_{i}.jpg"
                aug_img_path = os.path.join(aug_images_dir, aug_img_file)
                
                aug_lbl_path = os.path.join(aug_labels_dir, aug_img_file.replace('.jpg', '.txt'))
                
                aug_img.save(aug_img_path)
                
                with open(aug_lbl_path, 'w') as file:
                    file.writelines(aug_lbl)
                #aug_img_file是什么内容
                augmented_images.append(aug_img_file)
        else:
            no_target_images.append(img_file)
    except Exception as e:
        print(f"Error processing {img_file}: {e}")

# 打印有目标和无目标图像的数量
print(f"Number of images with targets: {len(augmented_images)}")
print(f"Number of images without targets: {len(no_target_images)}")

# 用户输入降采样比例
keep_no_target_ratio = 0.0  # 修改为用户输入值
keep_no_target = int(len(augmented_images) * keep_no_target_ratio)  # 保留指定比例的无目标图像
random.shuffle(no_target_images)
no_target_images = no_target_images[:keep_no_target]
augmented_images.extend(no_target_images)

# 随机分割数据集
random.shuffle(augmented_images)
train_split = int(0.7 * len(augmented_images))
val_split = int(0.85 * len(augmented_images))
# augmented_images里面保存的是什么？
for i, img_file in enumerate(tqdm(augmented_images, desc="Splitting dataset")):
    src_img_path = os.path.join(aug_images_dir, img_file)
    src_txt_path = os.path.join(aug_labels_dir, img_file.replace(".jpg",".txt"))
    
    if i < train_split:
        dst_dir = train_dir
    elif i < val_split:
        dst_dir = val_dir
    else:
        dst_dir = test_dir
        
    try:
        shutil.copy(src_img_path, os.path.join(dst_dir, "images", img_file))
        shutil.copy(src_txt_path, os.path.join(dst_dir, "labels", img_file.replace('.jpg', '.txt')))
    except Exception as e:
        print(f"Error copying {img_file}: {e}")
