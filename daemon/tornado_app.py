from tornado import web, websocket, ioloop
import subprocess
import json
import os


def make_app():
    return web.Application([
        (r"/web_socket/", WebHandler),
        (r"/scanner_status/", ScannerHandler),
    ])


class WebHandler(websocket.WebSocketHandler):
    waiter = None

    def check_origin(self, origin):
        return True

    def open(self):
        if WebHandler.waiter is None:
            WebHandler.waiter = self
        else:
            self.write_message(json.dumps({'msg': 'Error: Double'}))
            self.close()
            
    @classmethod
    def send_message(cls, code):
        check_code = {'code': code}
        cls.waiter.write_message(json.dumps(cls.check_code))

    def on_message(self, messsage):
        self.data = json.loads(messsage)
        wx_scan_app = os.path.abspath(os.path.join(os.getcwd(), '..', 'scanner', 'dist', 'wx_scanner.app'))
        #subprocess.call(["open", "-a", wx_scan_app])
        subprocess.Popen(["open", "-a", wx_scan_app])
        os.system(wx_scan_app)

    def on_close(self):
        if WebHandler.waiter is self:
            WebHandler.waiter = None
        

class ScannerHandler(web.RequestHandler):
    def get(self):
        save_code = self.get_arguments("code")
        server = ioloop.IOLoop.current()
        server.add_callback(WebHandler.send_message, save_code)
        self.set_status(200)
        self.finish()


if __name__ == '__main__':
    app = make_app()
    app.listen("8000", address="0.0.0.0")
    ioloop.IOLoop.current().start()
