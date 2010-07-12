#!/usr/bin/python
# -*- coding: utf-8 -*-

# a testament to all the hoops Python makes us jump through

import inspect
import runpy
import sys
import os.path

if len(sys.argv) < 2:
  print "Usage: runexample.py <filename>"
  print "Example: runexample.py examples/analysis.py"
  sys.exit()

f = sys.argv[1]
module = inspect.getmodulename(f)
if module is None:
  module = f
else:
  module = "%s.%s" % (f[:f.rfind(os.path.sep)], module)
runpy.run_module(module)
