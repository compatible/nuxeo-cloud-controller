import sys, os

#
# Utilities
#
def system(cmd):
  print cmd
  ret = os.system(cmd)
  if ret:
    print "Error, exiting."
    sys.exit()
