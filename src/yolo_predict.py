from ultralytics import YOLO
import preprocess_dicom
import os
import shutil
from PIL import Image

def generate_png(dicom_root,png_dir):
    os.makedirs(png_dir, exist_ok=True)
    png_root, sop = preprocess_dicom.translate_single_dicom(dicom_root, png_dir)
    return os.path.abspath(png_root)

def predict_and_crop_nodules(png_root, model, predict_dir, nodules_detail_dir):
    print("正在预测。。。")
    # Run prediction
    metrics = model.predict([png_root], save=True)
    result = metrics[0]
    boxes = result.boxes

    # Move the prediction image to the predict_dir
    path = result.path
    name = os.path.basename(path)
    save_dir = result.save_dir
    src_path = os.path.join(save_dir, name)
    dst_path = os.path.join(predict_dir,name)
    
    shutil.move(src_path, dst_path)

    # Open the original image
    image = Image.open(png_root)
    nodule_paths = {}

    # Process each bounding box
    for i, box in enumerate(boxes.xywh):
        x_center, y_center, width, height = box.tolist()
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)
        
        cropped_image = image.crop((x1, y1, x2, y2))
        nodule_path = os.path.join(nodules_detail_dir, f"nodule_{i}.png")
        cropped_image.save(nodule_path)
        nodule_paths[f"Nodule{i}"] = os.path.abspath(nodule_path)

    return os.path.abspath(dst_path), nodule_paths

if __name__ == "__main__":
    dicom_path = "000002.dcm"
    png_root = generate_png(dicom_path)

    # Load YOLOv8 model
    model = YOLO("best.pt")
    predict_dir = "../output/prediction.png"
    nodules_detail_dir = "../output/nodules"
    
    os.makedirs(os.path.dirname(predict_dir), exist_ok=True)
    
    os.makedirs(nodules_detail_dir, exist_ok=True)

    # Predict and save the results
    prediction_image_path, nodule_paths = predict_and_crop_nodules(png_root, model, predict_dir, nodules_detail_dir)
    print(f"Prediction image saved at: {prediction_image_path}")
    print(f"Nodule paths: {nodule_paths}")
