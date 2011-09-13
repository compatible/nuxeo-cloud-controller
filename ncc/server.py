from model import *

#
# Web service
#
from flask import Flask, g
app = Flask(__name__)

@app.before_request
def connect_db():
  g.session = Session()

@app.route("/ping/<iid>")
def ping(iid):
  iid = int(iid)
  instance = g.session.query(Instance).filter_by(iid=iid).first()
  if instance is None:
    raise Exception("Instance %d does not exist." % iid)
  instance.start()
  g.session.commit()
  return "Please wait a few seconds and hit <refresh> (CRTL-R)."


def run():
  app.run(port=8000, debug=True)
