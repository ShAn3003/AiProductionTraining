import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.web import URLSpec
import os
import time 
import preprocess_dicom

class DetectLungNudules(object):
    def __init__(self,default_image_path,static_path):
        
        default_image_path = self.generateStaticPath(default_image_path)
        self.staticpath = static_path
        self.dicomfilepath=default_image_path
        self.originimgpath=default_image_path
        self.visualimgpath=default_image_path
        self.choosedimgpath=default_image_path
        
        
        self.dicomfilepath_s=default_image_path
        self.originimgpath_s=default_image_path
        self.visualimgpath_s=default_image_path
        self.choosedimgpath_s=default_image_path
        
        self.Nudulescount=3
        self.Nudulespath={}
        
    def setDicom(self,path):
        
        self.dicomfilepath=path
        
        png_dirctory = os.path.join(self.staticpath,'Png')
        if not os.path.exists(png_dirctory):
            os.makedirs(png_dirctory)
            
        self.originimgpath,_ = preprocess_dicom.translate_single_dicom(self.dicomfilepath,png_dirctory)
        
        self.originimgpath_s=self.generateStaticPath(self.originimgpath)
        
    def getDicom(self):
        return self.dicomfilepath
    
    def detectNudules(self):
        
        self.Nudulescount = 3
        self.visualimgpath = ""
        self.Nudulespath['Nodule0']=" "
    
    def generateStaticPath(self,path):
        filename = os.path.basename(path)
        dirctory = os.path.dirname(path)
        fa_dir = os.path.basename(dirctory)
        return f"/static/{fa_dir}/{filename}"
        
        

class MainHandler(tornado.web.RequestHandler):
    
    def initialize(self,dicom):
        print("initialize")
        self.dicom = dicom
        
    def get(self):
        self.render("../index/index.htm",origin_image_path = self.dicom.originimgpath_s,visualized_image_path=self.dicom.visualimgpath_s,count=self.dicom.Nudulescount, choosed_image_path=self.dicom.choosedimgpath_s)
        
        
    def post(self):
        uploaded_file = self.request.files.get("dicomfile",None)
        
        if uploaded_file:
            
            file_info=uploaded_file[0]
            
            filename = f"{int(time.time())}_{file_info['filename']}"
            body = file_info['body']
            
            upload_dir = os.path.join(self.settings['static_path'], "uploads")
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            dicomfile_path = os.path.join(upload_dir, filename)
            
            with open(dicomfile_path, 'wb') as f:
                f.write(body)
            
            self.dicom.setDicom(dicomfile_path)
            
            self.dicom.detectNudules()
            
            # 重定向到GET请求，并携带新的图片路径参数
            self.redirect(f"/?origin_image_path={self.dicom.originimgpath_s}&visualized_image_path={self.dicom.visualimgpath_s}&count={self.dicom.Nudulescount}&choosed_image_path={self.dicom.choosedimgpath_s}")
        else:
            self.write("No file uploaded.")

class SelectHandler(tornado.web.RequestHandler):
    def initialize(self,dicom):
        print("select_initialize")
        self.dicom = dicom
        
    def post(self):
        nodule = self.get_argument("nodule", None)
        if nodule:
            self.redirect(f"/?origin_image_path={self.dicom.originimgpath_s}&visualized_image_path={self.dicom.visualimgpath_s}&count={self.dicom.Nudulescount}&choosed_image_path={self.dicom.choosedimgpath_s}")
        else:
            self.write("No nodule selected.")


        
if __name__ == "__main__":
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    static_path=os.path.join(path, "static")
    default_image_path =  os.path.join(static_path,"default","default.png")
    
    print(static_path)
    
    dicom = DetectLungNudules(default_image_path=default_image_path,static_path=static_path)
    
    app = tornado.web.Application([
        URLSpec(r"/", MainHandler,{"dicom":dicom}),
        URLSpec(r"/select", SelectHandler,{"dicom":dicom}),
    ],static_path=static_path)
    
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    print("Server is running on port 8080")
    tornado.ioloop.IOLoop.current().start()

