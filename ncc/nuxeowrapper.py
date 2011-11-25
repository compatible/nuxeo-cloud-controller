#!/usr/bin/env python

##############################################################################
#
# Copyright (c) 2007 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################


""" Wrapper that know how to kill both the nuxeo launcher and the nuxeo process.

Might not be needed after all."""

import os
import sys
import signal
import time
from config import *


class NuxeoWrapper(object):

    def __init__(self, iid):
        self.setsignals()
        self.command = "%s/%d/bin/nuxeoctl" % (INSTANCES_HOME, iid)
        self.pidfile = "%s/%d/log/nuxeo.pid" % (INSTANCES_HOME, iid)
        self.cmdargs = [self.command, "console"]
        # The direct child pid
        self.pid = None

    def go(self):
        self.pid = os.spawnv(os.P_NOWAIT, self.command, self.cmdargs)
        while 1:
            time.sleep(5)
            try:
                pid, sts = os.waitpid(-1, os.WNOHANG)
            except OSError:
                pid, sts = None, None
            if pid:
                break

    def setsignals(self):
        signal.signal(signal.SIGTERM, self.passtochild)
        signal.signal(signal.SIGHUP, self.passtochild)
        signal.signal(signal.SIGINT, self.passtochild)
        signal.signal(signal.SIGUSR1, self.passtochild)
        signal.signal(signal.SIGUSR2, self.passtochild)
        signal.signal(signal.SIGCHLD, self.reap)

    def reap(self, sig, frame):
        # do nothing, we reap our child synchronously
        pass

    def passtochild(self, sig, frame):
        try:
            pid = int(open(self.pidfile, 'r').read().strip())
        except:
            pid = None
            print "Can't read child pidfile %s!" % self.pidfile
            return
        os.kill(self.pid, sig)
        os.kill(pid, sig)
        if sig in [signal.SIGTERM, signal.SIGINT, signal.SIGQUIT]:
            sys.exit(0)


def main():
    try:
        iid = int(sys.argv[1])
    except ValueError:
        print "nuxeowrapper <iid>"
        sys.exit(1)

    pp = NuxeoWrapper(iid)
    pp.go()

if __name__ == '__main__':
    main()
