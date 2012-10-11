import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class IndexHtml(tornado.web.RequestHandler):
    def get(self):
        self.write(file("index.html").read())

class IndexJs(tornado.web.RequestHandler):
    def get(self):
        self.write(file("index.js").read())



application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/index.html", IndexHtml),
    (r"/index.js", IndexJs),

])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

