from model import *
from util import system
import server

import os

#
# Commands
#
def cmd_clean():
  """Drop database and remove all instances (useful for debugging).
  """
  for instance in all_instances():
    if instance.state == RUNNING:
      instance.stop()
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

  for instance in all_instances():
    instance.setup_nginx_config(reload=False)

  start_nginx()


def cmd_halt():
  """Shutdown the system.
  """
  for instance in all_instances():
    if instance.state == RUNNING:
      instance.stop()
  # TODO: stop postgresql
  if is_nginx_running():
    stop_nginx()


def cmd_create():
  """Creates (and starts) a new instance.
  """
  instance = Instance()
  session.add(instance)
  session.commit()
  print "Creating new instance with id: %d" % instance.iid

  instance.setup()
  print "New instance created with id: %d" % instance.iid
  session.commit()

  instance.start()
  session.commit()
  print "Instance %s started on port %d" % (instance.iid, instance.port)

  return instance


def cmd_start(iid):
  """Starts the given instance.
  """
  instance = get_instance(iid)
  if instance.state != READY:
    raise Exception("Can't start an instance that is not ready")
  instance.start()
  session.commit()
  print "Instance %d started on port %d" % (instance.iid, instance.port)


def cmd_stop(iid):
  """Stops the given instance.
  """
  instance = get_instance(iid)
  if instance.state != RUNNING:
    raise Exception("Can't stop an instance that is not running")
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


def cmd_monitor():
  """Scans all the instances and stops those that can be stopped.
  """
  for instance in all_instances():
    instance.monitor()
  session.commit()


def cmd_serve():
  """Start web server on port 8000.
  """
  server.run()


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
  print "Usage: ncc <command> <args>"
  print
  print "where <command> can be:\n"
  names = globals().keys()
  names.sort()
  for name in names:
    if not name.startswith("cmd_"):
      continue
    print "- " + name[4:] + ": " + globals()[name].__doc__.strip()

