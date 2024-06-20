import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.web import URLSpec
import os
import time 
# import preprocess_dicom
from ultralytics import YOLO
from yolo_predict import predict_and_crop_nodules,generate_png

class DetectLungNodules(object):
    def __init__(self, model_path,visimg_dir,dicom_dir, default_image_path, static_path,original_path,predict_path,nodules_dir):
        
        print("正在加载模型。。。")
        self.model = YOLO(model_path)  # Load your YOLOv8 model
        print("加载完毕。。。")
        
        self.staticPath = static_path
        
        self.dicomDir = dicom_dir
        self.nodulesDir = nodules_dir
        self.visImgDir = visimg_dir
        
        self.dicomPath = default_image_path
        self.oriImgPath = default_image_path
        self.visImgPath = default_image_path
        self.chooseImgPath = default_image_path
        
        self.dicomPath_s = self.generateStaticPath(default_image_path)
        self.oriImgPath_s = self.generateStaticPath(default_image_path)
        self.visImgPath_s = self.generateStaticPath(default_image_path)
        self.chooseImgPath_s = self.generateStaticPath(default_image_path)
        
        self.nodulesCount = 0
        self.nodulesDict = {}

    def setDicomPath(self, path):
        self.dicomPath = path
        self.dicomPath_s = self.generateStaticPath(path)

    def setOripath(self, path):
        self.oriImgPath = path
        self.oriImgPath_s = self.generateStaticPath(path)

    def setVisImgPath(self, path):
        self.visImgPath = path
        self.visImgPath_s = self.generateStaticPath(path)

    def setCount(self, count):
        self.nodulesCount = count

    def setNoduledict(self, nodules):
        self.nodulesDict = {key: self.generateStaticPath(value) for key, value in nodules.items()}

    
    def detectNodules(self,dicom_path):
        # 完成各种文件的绝对路径的保存
        ori_img_dir = os.path.join(self.staticPath,"origin")
        ori_img_path = generate_png(dicom_root=dicom_path,png_dir=ori_img_dir)
        predict_img_path , nodules = predict_and_crop_nodules(png_root=ori_img_path,
                                                              model=self.model,
                                                              predict_dir=self.visImgDir,
                                                              nodules_detail_dir=self.nodulesDir)
        
        self.setDicomPath(dicom_path)
        
        self.setOripath(ori_img_path)
        self.setVisImgPath(predict_img_path)
        
        self.setCount(len(nodules))
        self.setNoduledict(nodules)
        
    def generateStaticPath(self, path):
        return f"/static{path.replace(self.staticPath, '').replace(os.sep, '/')}"


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, dicom):
        self.dicom = dicom

    def get(self):
        self.render("../index/index.htm", 
                    origin_image_path=self.dicom.oriImgPath_s,
                    visualized_image_path=self.dicom.visImgPath_s,
                    count=self.dicom.nodulesCount,
                    choosed_image_path=self.dicom.chooseImgPath_s)

    def post(self):
        
        uploaded_file = self.request.files.get("dicomfile", None)
        
        #处理以及保存上传的dicom文件
        if uploaded_file:
            
            file_info = uploaded_file[0]
            filename = f"{int(time.time())}_{file_info['filename']}"
            body = file_info['body']

            upload_dir = self.dicom.dicomDir

            dicomfile_path = os.path.join(upload_dir, filename)
            with open(dicomfile_path, 'wb') as f:
                f.write(body)
            
            self.dicom.detectNodules(os.path.abspath(dicomfile_path))
            
            self.redirect(f"/?origin_image_path={self.dicom.oriImgPath_s}&visualized_image_path={self.dicom.visImgPath_s}&count={self.dicom.nodulesCount}&choosed_image_path={self.dicom.chooseImgPath_s}")
        else:
            self.write("No file uploaded.")

class SelectHandler(tornado.web.RequestHandler):
    def initialize(self, dicom):
        self.dicom = dicom

    def post(self):
        nodule = self.get_argument("nodule", None)
        if nodule:
            self.dicom.chooseImgPath_s = self.dicom.nodulesDict.get(nodule, self.dicom.oriImgPath_s)
            self.redirect(f"/?origin_image_path={self.dicom.oriImgPath_s}&visualized_image_path={self.dicom.visImgPath_s}&count={self.dicom.nodulesCount}&choosed_image_path={self.dicom.chooseImgPath_s}")
        else:
            self.write("No nodule selected.")

        
if __name__ == "__main__":
    
    #路径以及文件夹设置
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    static_path=os.path.join(path, "static")
    default_image_path =  os.path.join(static_path,"default","default.png")
    predict_path = os.path.join(static_path,"predict","predict.png")
    original_path = os.path.join(static_path,"origin","origin.png")
    
    nodules_dir = os.path.join(static_path,"details")
    dicom_dir = os.path.join(static_path,"uploads")
    visimg_dir = os.path.join(static_path,"predict")
    
    os.makedirs(static_path,exist_ok=True)
    os.makedirs(os.path.dirname(default_image_path),exist_ok=True)
    os.makedirs(os.path.dirname(original_path),exist_ok=True)
    
    os.makedirs(visimg_dir,exist_ok=True)
    os.makedirs(nodules_dir,exist_ok=True)
    os.makedirs(dicom_dir,exist_ok=True)
    
    print(static_path)
    
    #yolo模型加载
    model_path = "best.pt"
    
    dicom = DetectLungNodules(model_path=model_path,
                              dicom_dir=dicom_dir,
                              visimg_dir=visimg_dir,
                              default_image_path=default_image_path,
                              static_path=static_path,
                              original_path=original_path,
                              predict_path=predict_path,
                              nodules_dir=nodules_dir)
    
    app = tornado.web.Application([
        URLSpec(r"/", MainHandler,{"dicom":dicom}),
        URLSpec(r"/select", SelectHandler,{"dicom":dicom}),
    ],static_path=static_path)
    
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    print("Server is running on port 8080")
    tornado.ioloop.IOLoop.current().start()

