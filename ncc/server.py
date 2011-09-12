from model import *

#
# Web service
#
from flask import Flask, g
app = Flask(__name__, static_path='/media')

@app.before_request
def connect_db():
  g.session = Session()

@app.route("/ping/<iid>")
def ping(iid):
  instance = get_instance(int(iid))
  instance.start()
  return "Please wait a few seconds and hit <refresh> (CRTL-R)."

def run():
  app.run(port=8000, debug=True)
