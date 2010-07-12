#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect
import runpy
import sys

if len(sys.argv) < 2:
  print "Usage: runexample.py <filename>"
  print "Example: runexample.py examples/example_data.py"
  sys.exit()

f = sys.argv[1]
module = inspect.getmodulename(f)
if module == None:
  module = f
runpy.run_module(module)
