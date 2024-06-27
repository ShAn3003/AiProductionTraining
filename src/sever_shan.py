import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.web import URLSpec
import os
import time
import shutil
import signal
import atexit
from detect import DetectLungNodules

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, dicom):
        self.dicom = dicom

    def get(self):
        error_message = self.get_argument("error", None)
        origin_image_path = self.get_argument("origin_image_path", self.dicom.oriImgPath_s)
        visualized_image_path = self.get_argument("visualized_image_path", self.dicom.visImgPath_s)
        count = self.get_argument("count", self.dicom.nodulesCount)
        choosed_image_path = self.get_argument("choosed_image_path", self.dicom.chooseImgPath_s)

        try:
            count = int(count)  # Ensure count is an integer
        except ValueError:
            count = 0

        self.render("../index/gptenhance.htm", 
                    origin_image_path=origin_image_path,
                    visualized_image_path=visualized_image_path,
                    count=count,
                    choosed_image_path=choosed_image_path,
                    error_message=error_message)

class DetectHandler(tornado.web.RequestHandler):
    def initialize(self, dicom):
        self.dicom = dicom

    def post(self):
        uploaded_file = self.request.files.get("dicomfile", None)
        
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
            self.redirect("/?error=No file uploaded.")

class SelectHandler(tornado.web.RequestHandler):
    def initialize(self, dicom):
        """
        初始化函数，将传入的dicom对象赋值给实例变量self.dicom。
        
        Args:
            dicom: 一个包含dicom信息的对象，通常是pydicom库读取的dicom文件对象。
        
        Returns:
            无返回值，但会将传入的dicom对象赋值给实例变量self.dicom。
        
        """
        self.dicom = dicom

    def post(self):
        """
        处理POST请求，根据提供的结节名称选择对应的DICOM图像进行可视化展示。
        
        Args:
            无参数，通过请求体中的表单数据传递参数。
        
        Returns:
            无返回值，直接通过HTTP重定向至新的URL。
        
        """
        nodule = self.get_argument("nodule", None)
        if nodule:
            self.dicom.chooseImgPath_s = self.dicom.nodulesDict.get(nodule, self.dicom.oriImgPath_s)
            self.redirect(f"/?origin_image_path={self.dicom.oriImgPath_s}&visualized_image_path={self.dicom.visImgPath_s}&count={self.dicom.nodulesCount}&choosed_image_path={self.dicom.chooseImgPath_s}")
        else:
            self.redirect("/?error=No nodule selected.")

def cleanup():
    directories_to_clean = [
        dicom.getDicomDir(),
        dicom.getOriginDir(),
        dicom.getVisImgDir(),
        dicom.getNodulesDir(),
        "runs"
    ]
    for directory in directories_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    print("Cleanup completed.")
    
def signal_handler(signum, frame):
    """
    处理系统信号并清理资源，然后停止Tornado的I/O循环。
    
    Args:
        signum (int): 接收到的系统信号编号。
        frame (types.FrameType): 当前的调用栈帧，通常不直接使用。
    
    Returns:
        None: 此函数没有返回值，主要用于处理系统信号。
    
    """
    print(f"Signal {signum} received, cleaning up...")
    cleanup()
    tornado.ioloop.IOLoop.current().stop()
      
if __name__ == "__main__":
    #路径以及文件夹设置
    path = os.path.dirname(os.path.dirname(__file__))
    static_dir=os.path.join(path, "static")
    
    default_dir = os.path.join(static_dir,"default")
    dicom_dir = os.path.join(static_dir,"uploads")
    origin_dir = os.path.join(static_dir,"origin")
    visimg_dir = os.path.join(static_dir,"predict")
    nodules_dir = os.path.join(static_dir,"details")
    
    os.makedirs(static_dir,exist_ok=True)
    os.makedirs(default_dir,exist_ok=True)
    os.makedirs(origin_dir,exist_ok=True)
    os.makedirs(visimg_dir,exist_ok=True)
    os.makedirs(nodules_dir,exist_ok=True)
    os.makedirs(dicom_dir,exist_ok=True)
    
    default_path =  os.path.join(default_dir,"default.png")
    print("default:",default_dir)
    print("static:",static_dir)
    print("dicom:",dicom_dir)
    print("origin:",origin_dir)
    print("visimg:",visimg_dir)
    
    #yolo模型加载
    model_path = "../Train_Yolo/LungNudulesDetect_yolov8m_100epochs\\100_epoches_formal\\weights\\best.pt"
    
    dicom = DetectLungNodules(static_dir=static_dir,
                              default_dir=default_dir,
                              origin_dir=origin_dir,
                              dicom_dir=dicom_dir,
                              visimg_dir=visimg_dir,
                              nodules_dir=nodules_dir,
                              model_path=model_path,
                              original_path=default_path,
                              predict_path=default_path,
                              default_path=default_path)
    
    app = tornado.web.Application([
        URLSpec(r"/", MainHandler, {"dicom": dicom}),
        URLSpec(r"/detect", DetectHandler, {"dicom": dicom}),
        URLSpec(r"/select", SelectHandler, {"dicom": dicom}),
    ], static_path=static_dir)
    
    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    print("Server is running on port 8080")
    tornado.ioloop.IOLoop.current().start()
