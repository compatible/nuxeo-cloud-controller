#!/usr/bin/env python
import urllib
import time

from ncc import *
from unittest import TestCase

class FunctionalTestCase(TestCase):

  def test(self):
    cmd_clean()
    cmd_boot()

    instances = cmd_list()
    instance_num = len(instances)

    instance = cmd_create()
    iid = instance.iid

    instances = cmd_list()
    self.assertEqual(instance_num+1, len(instances))

    cmd_start(iid)

    time.sleep(10)
    urllib.urlopen("http://localhost:%d/nuxeo/" % instance.port).read()

    cmd_stop(iid)
    cmd_destroy(iid)
    cmd_purge(iid)


