#
# Constants (move to config file later)
#

# Contains all the instances as well as the DB and nginx files
HOME = "/Users/fermigier/nuxeocloud/"

# The model (or template) that duplicated upon instance creation
MODEL = HOME + "models/nuxeo-dm-5.4.2-tomcat"

# You probably dont' want to touch these
INSTANCES_HOME = HOME + "instances/"
DB = HOME + "nuxeocloud.db"

# Port for nginx
PORT = 8080

# 60 seconds for now,
INACTIVITY_TIME = 60

# Pretty explicit
DEBUG = True

NGINX_CONF = """
#user  nobody;
daemon off;
worker_processes  1;

error_log ##HOME##/nginx/log/error.log info;
pid ##HOME##/nginx/nginx.pid;

events {
    worker_connections  1024;
}

http {
  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

  include "vhosts/*";
}
"""

