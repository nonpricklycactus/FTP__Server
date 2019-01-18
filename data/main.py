
import optparse
import socketserver
from conf import setting
from data import server

class ArgvHandler():
    def __init__(self):
        self.op =optparse.OptionParser()
        options,args =self.op.parse_args()

        self.verify_arg(options,args)

    def verify_arg(self,options,args):
        cmd =args[0]
        if hasattr(self,cmd):           #找到该类下与参数相同的函数
            func =getattr(self,cmd)
            func()

    def start(self):
        print("正在连接.......")
        s =socketserver.ThreadingTCPServer((setting.IP,setting.PORT),server.ServerHandler)
        s.serve_forever()