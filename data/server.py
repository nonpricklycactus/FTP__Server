import socketserver
import json
import configparser
from conf import setting
import os

STATUS_CODE  = {

    250 : "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251 : "Invalid cmd ",
    252 : "Invalid auth data",
    253 : "Wrong username or password",
    254 : "Passed authentication",
    255 : "Filename doesn't provided",
    256 : "File doesn't exist on server",
    257 : "ready to send file",
    258 : "md5 verification",

    800 : "the file exist,but not enough ,is continue? ",
    801 : "the file exist !",
    802 : " ready to receive datas",

    900 : "md5 valdate success"

}

class ServerHandler(socketserver.BaseRequestHandler):

    def handle(self):

        while True:
            data =self.request.recv(1024).strip()
            data =json.loads(data.decode("utf8"))

            '''"{ 
                "acton":"auth"
                "username":"asd"
                "password":123456
        }"'''

            if data.get("action"):

                if hasattr(self,data.get("action")):
                    func =getattr(self,data.get("action"))
                    func(**data)
                else:
                    print("Invaild cmd")

            else:
                print("Invaild cmd")


    def send_response(self,state_code):
        response ={"status_code":state_code}
        self.request.sendall(json.dumps(response).encode("utf8"))
        print("STATUS_CODE已发送！")

    def auth(self,**kwargs):

        username =kwargs["username"]
        password =kwargs["password"]

        user =self.authenticate(username,password)

        if user:
            self.send_response(254)
        else:
            self.send_response(253)

    def authenticate(self,user,pwd):
        cfg =configparser.ConfigParser()
        cfg.read(setting.ACCOUNT_PATH)

        if user in cfg.sections():
            if cfg[user]["Password"]==pwd:
                self.user =user
                self.mainPath =os.path.join(setting.BASE_DIR,"home",self.user)
                print("登陆成功！")
                return user



    def put(self,**kwargs):
        print("data:",kwargs)
        file_name =kwargs.get("file_name")
        file_size =kwargs.get("file_size")
        target_path =kwargs.get("target_path")

        abs_path =os.path.join(self.mainPath,target_path,file_name)

        ###文件上传会遇到的几种情况解决################################
        has_received =0
        if os.path.exists(abs_path):
            file_has_size =os.stat(abs_path).st_size
            if file_has_size<file_size:        #断点续传
                self.request.sendall("800".encode("utf8"))
                choice =self.request.recv(1024).decode("utf8")
                if choice=="Y":
                    self.request.sendall(str(file_has_size).encode("utf8"))
                    has_received+=file_has_size
                    f =open(abs_path,"ab")
                else: #不续传，重新写文件
                    f =open(abs_path,"wb")

            else:   #文件完全存在
                self.request.sendall("801".encode("utf8"))
                return

        else:
            self.request.sendall("802".encode("utf8"))
            f = open(abs_path, "wb")

        while has_received<file_size:
            data =self.request.recv(1024)
            f.write(data)
            has_received+=len(data)

        f.close()


    def ls(self,**kwargs):
        file_list =os.listdir(self.mainPath)

        file_str ="\n".join(file_list)
        if not  len(file_list):
            file_str ="<empty dir>"

        self.request.sendall(file_str.encode("utf8"))

    def cd(self,**kwargs):

        dirname =kwargs.get("dirname")

        if dirname=="..":
            self.mainPath =os.path.dirname(self.mainPath)
        else:
            self.mainPath =os.path.join(self.mainPath,dirname)

        self.request.sendall(self.mainPath.encode("utf8"))

    def mkdir(self,**kwargs):
        dirname =kwargs.get("dirname")

        path =os.path.join(self.mainPath,dirname)

        if not os.path.exists(path):
            if "/" in dirname:
                os.makedirs(path)
            else:
                os.mkdir(path)
            self.request.sendall("文件夹存在".encode("utf8"))
        else:
            self.request.sendall("文件夹存在".encode("utf8"))









