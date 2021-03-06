#!/usr/bin/env python

from ncc.config import PORT
from ncc.commands import *
from ncc.processes import supervisor

from unittest import TestCase
import urllib
import time


class FunctionalTestCase(TestCase):

  @classmethod
  def setUpClass(cls):
    cmd_clean()
    cmd_boot()

  @classmethod
  def tearDownClass(cls):
    cmd_halt()
    cmd_clean()

  def test(self):
    instances = cmd_list()
    instance_num = len(instances)

    instance = cmd_create()
    iid = instance.iid

    instances = cmd_list()
    self.assertEqual(instance_num+1, len(instances))

    time.sleep(10)
    urllib.urlopen("http://localhost:%d/nuxeo/" % instance.port).read()
    urllib.urlopen("http://%s:%d/nuxeo/" % (instance.hostname, PORT)).read()

    cmd_stop(iid)
    cmd_destroy(iid)
    cmd_purge(iid)


class SupervisorTestCase(TestCase):

  def test(self):
    supervisor.gen_conf()
    supervisor.start()
    time.sleep(5)
    supervisor.stop()
