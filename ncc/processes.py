# Note: this package is called "processes" and not "supervisor" to prevent collision with
# the supervisor package. Might not be needed actually. TODO: check this.

from util import system
from config import HOME

CONF = """
[unix_http_server]
file=%(HOME)s/supervisor.sock   ; (the path to the socket file)

[supervisord]
logfile=%(HOME)s/supervisord.log ; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB       ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10          ; (num of main logfile rotation backups;default 10)
loglevel=info               ; (log level;default info; others: debug,warn,trace)
pidfile=%(HOME)s/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=false              ; (start in foreground if true;default false)
minfds=1024                 ; (min. avail startup file descriptors;default 1024)
minprocs=200                ; (min. avail process descriptors;default 200)

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://%(HOME)s/supervisor.sock ; use a unix:// URL  for a unix socket

[program:nginx]
command=nginx -c %(HOME)s/nginx/nginx.conf
autostart=true

"""

class Supervisor(object):

  def start(self):
    system("supervisord -c %s/supervisor.conf" % HOME)

  def stop(self):
    system("supervisorctl -c %s/supervisor.conf shutdown" % HOME, ignore_err=True)

  def start_service(self, name):
    system("supervisorctl -c %s/supervisor.conf start %s" % (HOME, name))

  def stop_service(self, name):
    system("supervisorctl -c %s/supervisor.conf stop %s" % (HOME, name))

  def restart_service(self, name):
    system("supervisorctl -c %s/supervisor.conf restart %s" % (HOME, name))

  def reload(self):
    system("supervisorctl -c %s/supervisor.conf reload" % HOME)

  def gen_conf(self):
    print "!!! GENERATING SUPERVISOR CONF !!!"
    conf = CONF % {'HOME': HOME}

    from model import session, Instance, RUNNING, READY
    instances = session.query(Instance).all()
    for instance in instances:
      if instance.state in (RUNNING, READY):
        conf += "[program:%s]\n" % instance.name
        conf += "command=nuxeowrapper %d\n" % instance.iid
        conf += "autostart=false\n"
        conf += "stopsignal=INT\n"
        conf += "\n"

    fd = open("%s/supervisor.conf" % HOME, "wc")
    fd.write(conf)
    fd.close()

supervisor = Supervisor()
