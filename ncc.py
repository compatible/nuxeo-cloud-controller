#!/usr/bin/env python

import os, sys, getopt
from pprint import pformat
from datetime import datetime

#
# Constants (move to config file later)
#
HOME = "/Users/fermigier/nuxeocloud/"
MODEL = HOME + "models/nuxeo-dm-5.4.2-tomcat"
INSTANCES = HOME + "instances/"
DB = HOME + "nuxeocloud.db"
PORT = 8080

DEBUG = True
 
# States
CREATED = "CREATED"
READY = "READY"
RUNNING = "RUNNING"
DESTROYED = "DESTROYED"

# Do we need these?
#CREATED = 1
#STARTING = 3
#RUNNING = 4
#STOPPING = 5
#STOPPED = 6
#DESTROYED = 7

#
NGINX_UP = """
server {
  listen 8080;

  server_name %(hostname)s;
  access_log %(HOME)s/nginx/log/access-%(iid)d.log;

  location / {
    proxy_pass http://localhost:%(port)d;

    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Server $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $http_host;
    proxy_set_header nuxeo-virtual-host "http://%(hostname)s:8080/";
  }
}
"""

NGINX_DOWN = """
server {
  listen 8080;

  server_name %(hostname)s;
  access_log %(HOME)s/nginx/log/access-%(iid)d.log;

  location / {
    rewrite /nuxeo/.* /ping/%(iid)d last;
    proxy_pass http://localhost:8000;
  }
}
"""

#
# ORM part
#
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import create_engine
from sqlalchemy.schema import Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///' + DB) #, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

class Instance(Base):
  __tablename__ = "instance"

  # Instance id
  iid = Column(Integer, Sequence('instance_id_seq'), primary_key=True)
  state = Column(String(10))
  owner = Column(String(100))
  created = Column(DateTime, default=datetime.now)
  #port = Column(Integer)

  def __init__(self, owner=""):
    self.state = CREATED
    self.owner = owner

  def __repr__(self):
    return pformat(self.__dict__)

  ## Properties

  @property
  def home(self):
    return HOME + "instances/%d" % self.iid

  @property
  def user(self):
    return "nuxeo%d" % self.iid

  @property
  def hostname(self):
    return "nuxeo%d" % self.iid

  @property
  def db_user(self):
    # TODO
    return "nuxeo"

  @property
  def db_name(self):
    return "nuxeo%d" % self.iid

  @property
  def db_password(self):
    # TODO: generate and store random password
    return "nuxeo"

  @property
  def port(self):
    # TODO: too simple
    return 8080 + 100 * self.iid

  @property
  def admin_port(self):
    # TODO: too simple
    return 8085 + 100 * self.iid

  ## Setup and other management methods

  def setup(self):
    self.setup_files()
    self.setup_db()
    self.setup_config()

  def setup_files(self):
    system("cp -r %s %s" % (MODEL, self.home))
    system("rm -rf %s/nxserver/lib" % self.home)
    system("rm -rf %s/nxserver/bundles" % self.home)
    system("ln -sf %s/nxserver/lib %s/nxserver/lib" % (MODEL, self.home))
    system("ln -sf %s/nxserver/bundles %s/nxserver/bundles" % (MODEL, self.home))

  def setup_db(self):
    system("createdb %s" % self.db_name)

  def setup_config(self):
    config = open("%s/bin/nuxeo.conf" % self.home).read()
    config += "nuxeo.wizard.done=true\n"
    config += "nuxeo.templates=postgresql\n"
    config += "nuxeo.db.name=" + self.db_name + "\n"
    config += "nuxeo.db.user=" + self.db_user + "\n"
    config += "nuxeo.db.password=" + self.db_password + "\n"
    config += "nuxeo.server.http.port=" + str(self.port) + "\n"
    config += "nuxeo.server.tomcat-admin.port=" + str(self.admin_port) + "\n"
    config += "nuxeo.url=http://%s:%d/nuxeo\n" % (self.hostname, PORT)
    fd = open("%s/bin/nuxeo.conf" % self.home, "w")
    fd.write(config)
    fd.close()

  def start(self):
    if self.state == READY:
      system("%s/bin/nuxeoctl start" % self.home)

  def stop(self):
    if self.state == RUNNING:
      system("%s/bin/nuxeoctl stop" % self.home)
    self.state = READY

  def purge(self):
    system("rm -rf %s" % self.home)
    system("dropdb %s" % self.db_name)

  def start_proxying(self):
    vhost_conf = NGINX_UP % {
        'HOME': HOME,
        'iid': self.iid,
        'hostname': self.hostname,
        'port': self.port}
    fd = open("%s/nginx/vhosts/%s.conf" % (HOME, self.iid), "wc")
    fd.write(vhost_conf)
    fd.close()
    system("nginx -c %s/nginx/nginx.conf -s reload" % HOME)

  def stop_proxying(self):
    vhost_conf = NGINX_DOWN % {
        'HOME': HOME,
        'iid': self.iid,
        'hostname': self.hostname,
    }
    fd = open("%s/nginx/vhosts/%s.conf" % (HOME, self.iid), "wc")
    fd.write(vhost_conf)
    fd.close()
    system("nginx -c %s/nginx/nginx.conf -s reload" % HOME)


def get_instance(iid):
  iid = int(iid)
  instance = session.query(Instance).filter_by(iid=iid).first()
  if instance is None:
    raise Exception("Instance %d does not exist." % iid)
  return instance

def all_instances():
  return session.query(Instance).all()

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


#
# Commands
#
def cmd_clean():
  """Drop database and remove all instances (useful for debugging).
  """
  for instance in all_instances():
    instance.purge()
    session.delete(instance)
    session.commit()
    
  #os.unlink(DB)
  system("rm -rf %s/nginx" % HOME)

def cmd_boot():
  """Boot the system.
  """
  # TODO: setup/start postgresql
  if not os.path.exists("%s/nginx" % HOME):
    os.mkdir("%s/nginx" % HOME)
  if not os.path.exists("%s/nginx/vhosts" % HOME):
    os.mkdir("%s/nginx/vhosts" % HOME)
  if not os.path.exists("%s/nginx/log" % HOME):
    os.mkdir("%s/nginx/log" % HOME)
  nginx_conf = open("nginx.conf").read()
  nginx_conf = nginx_conf.replace("##HOME##", HOME)
  fd = open("%s/nginx/nginx.conf" % HOME, "wc")
  fd.write(nginx_conf)
  fd.close()

  system("nginx -c %s/nginx/nginx.conf" % HOME)


def cmd_halt():
  """Shutdown the system.
  """
  for instance in all_instances():
    instance.stop()
  # TODO: stop postgresql
  system("nginx -c %s/nginx/nginx.conf -s stop" % HOME)


def cmd_create():
  """Creates (and starts) a new instance.
  """
  instance = Instance()
  session.add(instance)
  session.commit()
  print "Creating new instance with id: %d" % instance.iid

  instance.setup()
  print "New instance created with id: %d" % instance.iid
  instance.state = READY
  session.commit()

  instance.start()
  instance.state = RUNNING
  session.commit()
  instance.start_proxying()
  print "Instance %s started on port %d" % (instance.iid, instance.port)

  return instance


def cmd_start(iid):
  """Starts the given instance.
  """
  instance = get_instance(iid)
  instance.start()
  instance.start_proxying()
  session.commit()
  print "Instance %d started on port %d" % (instance.iid, instance.port)


def cmd_stop(iid):
  """Stops the given instance.
  """
  instance = get_instance(iid)
  instance.stop_proxying()
  instance.stop()
  session.commit()
  print "Instance %d stopped" % instance.iid


def cmd_destroy(iid):
  """Destroys the given instance.
  """
  instance = get_instance(iid)
  if instance.state != READY:
    raise Exception("Can't destroy an instance that is not stopped")
  instance.state = DESTROYED
  session.commit()


def cmd_purge(iid):
  """Purge (deletes completely) the given instance.
  """
  instance = get_instance(iid)
  if instance.state != DESTROYED:
    raise Exception("Can't purge an instance that is not destroyed")
  instance.purge()
  session.delete(instance)
  session.commit()


def cmd_serve():
  """Start web server on port 8000.
  """
  app.run(port=8000, debug=True)


def cmd_list():
  """Lists the existing instances.
  """
  instances = all_instances()
  for instance in instances:
    print "Instance: %s" % instance.iid
    print instance
  return instances


def cmd_info(iid):
  """Detailed info about the given instance.
  """
  instance = get_instance(iid)
  print instance
  return instance


def cmd_help():
  """Help about command-line usage.
  """
  print "Usage: ncc.py <command> <args>"
  print
  print "where <command> can be:\n"
  names = globals().keys()
  names.sort()
  for name in names:
    if not name.startswith("cmd_"):
      continue
    print "- " + name[4:] + ": " + globals()[name].__doc__.strip()

#
# Utilities
#
def system(cmd):
  print cmd
  ret = os.system(cmd)
  if ret:
    print "Error, exiting."
    sys.exit()

#
# Main
#
def main(argv):
  opts, args = getopt.getopt(argv, "t:")
  options = {}
  cmd = args[0]
  for k, v in opts:
    if k == '-t':
      options['type'] = v
  fn = globals()['cmd_'+cmd]
  if len(args) > 1:
    fn(*args[1:], **options)
  else:
    fn(**options)
    
  
if __name__ == "__main__":
  if DEBUG:
    main(sys.argv[1:])
  else:
    try:
      main(sys.argv[1:])
    except Exception, e:
      print e.message
      sys.exit(1)
