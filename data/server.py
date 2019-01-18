import socketserver

class ServerHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print("ok")