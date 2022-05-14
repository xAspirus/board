import sqlite3

from rich import print
from flask import Flask

APP = Flask(__name__)
DB = sqlite3.connect(".db")


@APP.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    port = 8000
    print(f'Server starting at: http://0.0.0.0:{port}/')
    APP.run(host="0.0.0.0", port=port)
