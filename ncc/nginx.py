from util import *
from config import *
import psi.process
import time


def is_nginx_running():
  pid_path = "%s/nginx/nginx.pid" % HOME
  if not os.path.exists(pid_path):
    return False
  pid = int(open(pid_path).read())
  process_table = psi.process.ProcessTable()
  if not process_table.has_key(pid):
    return False
  return process_table[pid].name == 'nginx'

def start_nginx():
  assert not is_nginx_running()
  if not is_nginx_running():
    system("nginx -c %s/nginx/nginx.conf" % HOME)
    time.sleep(5)
  else:
    print "nginx already running"

def stop_nginx():
  assert is_nginx_running()
  if is_nginx_running():
    system("nginx -c %s/nginx/nginx.conf -s stop" % HOME)
  else:
    print "nginx not running"

def reload_nginx():
  assert is_nginx_running()
  if not is_nginx_running():
    print "nginx not running, starting it"
    system("nginx -c %s/nginx/nginx.conf" % HOME)
    time.sleep(5)
  else:
    try:
      system("nginx -c %s/nginx/nginx.conf -s reload" % HOME)
      time.sleep(5)
    except:
      print "nginx not running, starting it"
      system("nginx -c %s/nginx/nginx.conf" % HOME)
      time.sleep(5)

def setup_nginx():
  if not os.path.exists(HOME + "/nginx"):
    os.mkdir(HOME + "/nginx")
  if not os.path.exists(HOME + "/nginx/vhosts"):
    os.mkdir(HOME + "/nginx/vhosts")
  if not os.path.exists(HOME + "/nginx/log"):
    os.mkdir(HOME + "/nginx/log")
  nginx_conf = NGINX_CONF.replace("##HOME##", HOME)
  fd = open(HOME + "/nginx/nginx.conf", "wc")
  fd.write(nginx_conf)
  fd.close()
