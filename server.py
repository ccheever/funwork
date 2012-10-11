import tornado.ioloop
import tornado.web

import getpass
USER = getpass.getuser()

if USER == "aiba":
    PORT = 8880
elif USER == "ccheever":
    PORT = 8881
else:
    PORT = 8888



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class IndexHtml(tornado.web.RequestHandler):
    def get(self):
        self.write(file("index.html").read())

class IndexJs(tornado.web.RequestHandler):
    def get(self):
        self.write(file("index.js").read())

class IndexCss(tornado.web.RequestHandler):
    def get(self):
        self.write(file("index.css").read())

class Search(tornado.web.RequestHandler):
    def get(self):
        return "Placeholder for JSONified records"



application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/index.html", IndexHtml),
    (r"/index.js", IndexJs),
    (r"/index.css", IndexCss),
    (r"/search", Search),

])

if __name__ == "__main__":
    application.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()

