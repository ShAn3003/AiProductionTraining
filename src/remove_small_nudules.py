import os
from tqdm import tqdm

# 定义文件夹路径
image_folder = "../yolo/augmented_images"
label_folder = "../yolo/labels"

# 获取标签文件列表
label_files = os.listdir(label_folder)

# 使用 tqdm 遍历标签文件列表，显示进度条
for label_file in tqdm(label_files, desc="Processing files", unit="files"):
    label_path = os.path.join(label_folder, label_file)
    
    # 读取标签文件内容
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    # 检查是否所有边界框都只有一个像素点
    one_pixel_boxes = True
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        width = float(parts[3])
        height = float(parts[4])
        if width > 0.001 or height > 0.001:
            one_pixel_boxes = False
            break
    
    # 如果所有边界框都只有一个像素点，删除标签文件和对应的图像文件
    if one_pixel_boxes:
        # 删除标签文件
        
        os.remove(label_path)
        
        # 删除对应的图像文件
        image_file = label_file.replace('.txt', '.jpg')  # 假设图像文件扩展名为.jpg
        image_path = os.path.join(image_folder, image_file)
        if os.path.exists(image_path):
            os.remove(image_path)

# 输出完成信息
print("Finished processing files.")
