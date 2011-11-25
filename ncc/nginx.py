from util import *
from config import *
import psi.process


def is_nginx_running():
  pid_path = "%s/nginx/nginx.pid" % HOME
  if not os.path.exists(pid_path):
    return False
  pid = int(open(pid_path).read())
  process_table = psi.process.ProcessTable()
  if not pid in process_table:
    return False
  return process_table[pid].name == 'nginx'


def reload_nginx():
  if is_nginx_running():
    system("nginx -c %s/nginx/nginx.conf -s reload" % HOME)


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
