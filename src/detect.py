from ultralytics import YOLO
from yolo_predict import predict_and_crop_nodules,generate_png
import os

class DetectLungNodules(object):
    def __init__(self, model_path, default_dir, origin_dir, visimg_dir, dicom_dir, default_path, static_dir, original_path, predict_path, nodules_dir):
        print("Loading model...")
        self.modelPath = model_path
        self.model = YOLO(model_path)  # Load your YOLOv8 model
        print("Model loaded.")

        self.staticDir = static_dir
        self.defaultDir = default_dir
        self.originDir = origin_dir
        self.dicomDir = dicom_dir
        self.nodulesDir = nodules_dir
        self.visImgDir = visimg_dir

        self.dicomPath = default_path
        self.oriImgPath = default_path
        self.visImgPath = default_path
        self.chooseImgPath = default_path

        self.dicomPath_s = self.generatestaticDir(default_path)
        self.oriImgPath_s = self.generatestaticDir(default_path)
        self.visImgPath_s = self.generatestaticDir(default_path)
        self.chooseImgPath_s = self.generatestaticDir(default_path)

        self.nodulesCount = 0
        self.nodulesDict = {}

#get function for all variations
    # dir getter
    def getStaticDir(self):
        return self.staticDir

    def getDefaultDir(self):
        return self.defaultDir

    def getOriginDir(self):
        return self.originDir

    def getDicomDir(self):
        return self.dicomDir

    def getNodulesDir(self):
        return self.nodulesDir

    def getVisImgDir(self):
        return self.visImgDir

    #absolute path getter
    def getDicomPath(self):
        return self.dicomPath

    def getOriImgPath(self):
        return self.oriImgPath

    def getVisImgPath(self):
        return self.visImgPath

    def getChooseImgPath(self):
        return self.chooseImgPath

    #static path getter
    def getDicomPath_s(self):
        return self.dicomPath_s

    def getOriImgPath_s(self):
        return self.oriImgPath_s

    def getVisImgPath_s(self):
        return self.visImgPath_s

    def getChooseImgPath_s(self):
        return self.chooseImgPath_s

    #nodules count getter
    def getNodulesCount(self):
        return self.nodulesCount

    #nodules detail static path getter
    def getNodulesDict(self):
        return self.nodulesDict
    
#set function for all path variation
    def setDicomPath(self, path):
        self.dicomPath = path
        self.dicomPath_s = self.generatestaticDir(path)

    def setOripath(self, path):
        self.oriImgPath = path
        self.oriImgPath_s = self.generatestaticDir(path)

    def setVisImgPath(self, path):
        self.visImgPath = path
        self.visImgPath_s = self.generatestaticDir(path)

    def setChooseImgPath(self, path):
        self.chooseImgPath = path
        self.chooseImgPath_s = self.generatestaticDir(path)

    def setCount(self, count):
        self.nodulesCount = count

    def setNoduledict(self, nodules):
        self.nodulesDict = {key: self.generatestaticDir(value) for key, value in nodules.items()}

    
    def detectNodules(self,dicom_path):
        # 完成各种文件的绝对路径的保存
        
        self.setDicomPath(dicom_path)
        
        ori_img_path = generate_png(dicom_root=self.dicomPath,png_dir=self.originDir)
        
        self.setOripath(ori_img_path)
        
        predict_img_path , nodules = predict_and_crop_nodules(model=self.model,
                                                              png_root=self.oriImgPath,
                                                              predict_dir=self.visImgDir,
                                                              nodules_detail_dir=self.nodulesDir)
        
        self.setVisImgPath(predict_img_path)
        
        self.setCount(len(nodules))
        self.setNoduledict(nodules)
        
    def generatestaticDir(self, path):
        return f"/static{path.replace(self.staticDir, '').replace(os.sep, '/')}"
