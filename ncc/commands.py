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

