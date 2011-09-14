from config import *
from util import *

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import create_engine
from sqlalchemy.schema import Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from datetime import datetime
from pprint import pformat

# States
CREATED = "CREATED"
READY = "READY"
RUNNING = "RUNNING"
DESTROYED = "DESTROYED"

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

Base = declarative_base()
engine = create_engine('sqlite:///' + DB) #, echo=True)
Session = sessionmaker(engine)
session = Session()

class Instance(Base):
  __tablename__ = "instance"

  # Instance id
  iid = Column(Integer, Sequence('instance_id_seq'), primary_key=True)
  state = Column(String(10))
  owner = Column(String(100))
  name = Column(String(30), unique=True, nullable=False)
  created = Column(DateTime, default=datetime.now)
  #port = Column(Integer)

  def __init__(self, name="", owner=""):
    self.state = READY
    self.name = name
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

  def setup_nginx_config(self, reload=True):
    conf_path = "%s/nginx/vhosts/%s.conf" % (HOME, self.iid)
    if not self.state in (RUNNING, READY):
      if os.path.exists(conf_path):
        os.unlink(conf_path)
      return

    if self.state == RUNNING:
      vhost_conf = NGINX_UP % {
          'HOME': HOME,
          'iid': self.iid,
          'hostname': self.hostname,
          'port': self.port}
    else:
      vhost_conf = NGINX_DOWN % {
          'HOME': HOME,
          'iid': self.iid,
          'hostname': self.hostname,
      }
    fd = open(conf_path, "wc")
    fd.write(vhost_conf)
    fd.close()
    if reload:
      reload_nginx()

  def start(self):
    if self.state == READY:
      system("%s/bin/nuxeoctl start" % self.home)
    else:
      raise Exception("Not ready")
    self.state = RUNNING
    self.setup_nginx_config()

  def stop(self):
    if self.state == RUNNING:
      system("%s/bin/nuxeoctl stop" % self.home)
    else:
      raise Exception("Not running")
    self.state = READY
    self.setup_nginx_config()

  def purge(self):
    system("dropdb %s" % self.db_name, ignore_err=True)
    system("rm -rf %s" % self.home)

  def monitor(self):
    if not self.state == RUNNING:
      return
    log_file = "%s/nginx/log/access-%s.log" % (HOME, self.iid)
    last_hit_time = os.stat(log_file).st_mtime
    if time.time() - last_hit_time > INACTIVITY_TIME:
      print "Putting instance %s to sleep" % self.iid
      self.stop()

def get_instance(iid):
  iid = int(iid)
  instance = session.query(Instance).filter_by(iid=iid).first()
  if instance is None:
    raise Exception("Instance %d does not exist." % iid)
  return instance

def all_instances():
  return session.query(Instance).all()

