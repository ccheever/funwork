import getpass
import os

from flask import Flask
app = Flask(__name__)

USER = getpass.getuser()
if USER == "aiba":
    PORT = 8880
elif USER == "ccheever":
    PORT = 8881
else:
    PORT = 5000

def local_file(file_name):
    return file(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), file_name)).read()

@app.route('/')
def hello_world():
    return 'Hello zoom!'

@app.route("/index.html")
def index_html():
    return local_file("index.html")

@app.route("/index.css")
def index_css():
    return local_file("index.css")

@app.route("/index.js")
def index_js():
    return local_file("index.js")

if __name__ == '__main__':
    app.run(debug=True, port=PORT, host="0.0.0.0")

