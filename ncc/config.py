#
# Constants (move to config file later)
#

# Contains all the instances as well as the DB and nginx files
HOME = "/Users/fermigier/nuxeocloud/"

# The model (or template) that duplicated upon instance creation
MODEL = HOME + "models/nuxeo-dm-5.4.2-tomcat"

# You probably dont' want to touch these
INSTANCES = HOME + "instances/"
DB = HOME + "nuxeocloud.db"

# Port for nginx
PORT = 8080

# 60 seconds for now,
INACTIVITY_TIME = 60

# Pretty explicit
DEBUG = True
