import os

#
# Utilities
#
def system(cmd, ignore_err=False):
  print cmd
  ret = os.system(cmd)
  if ret and not ignore_err:
    print "Error, exiting."
    raise Exception("Shell command exited with error")

