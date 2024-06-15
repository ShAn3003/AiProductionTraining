import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import time
from time import sleep

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        origin_image_path = self.get_argument("origin_image_path","/static/image/SimpleITK.png")
        visualized_image_path = self.get_argument("visualized_image_path", "/static/image/SimpleITK.png")
        count = self.get_argument("count", 2)
        choosed_image_path = self.get_argument("choosed_image_path", "/static/image/SimpleITK.png")
        self.render("../index/index.htm",origin_image_path = origin_image_path,visualized_image_path=visualized_image_path,count=count, choosed_image_path=choosed_image_path)
        
    def post(self):
        uploaded_file = self.request.files.get("dicomfile",None)
        if uploaded_file:
            
            file_info=uploaded_file[0]
            filename = f"{int(time.time())}_{file_info['filename']}"
            body = file_info['body']
             # 保存上传的文件到uploads目录
            upload_dir = os.path.join(self.settings['static_path'], "uploads")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(body)
            
            # 生成新的图片路径
            origin_image_path = f"/static/uploads/{filename}"
            
            # 重定向到GET请求，并携带新的图片路径参数
            self.redirect(f"/?origin_image_path={origin_image_path}")
        else:
            self.write("No file uploaded.")

class SelectHandler(tornado.web.RequestHandler):
    def post(self):
        nodule = self.get_argument("nodule", None)
        if nodule:
            print(nodule)
            # 假设你有对应结节的详细图片路径，这里只是一个示例
            choosed_image_path = f"/static/image/SimpleITK.png"
            # 重定向到GET请求，并携带选择的结节图片路径参数
            self.redirect(f"/?choosed_image_path={choosed_image_path}")
        else:
            self.write("No nodule selected.")


        
if __name__ == "__main__":
    
    static_path=os.path.join(os.path.dirname(__file__), "../static")
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/select", SelectHandler),
    ],static_path=static_path)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    print("Server is running on port 8080")
    tornado.ioloop.IOLoop.current().start()

