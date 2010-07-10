#!/usr/bin/python
# -*- coding: utf-8 -*-

from itertools import product
from collections import defaultdict
import re

class CPLogicGenerator:
  def generate(self,model):
    code = []
    links = model.getLinks()
    linksdict = defaultdict(list)
    for (s,d) in links:
      linksdict[d].append(s)
    for (d,ss) in linksdict.items():
      head = self.makeHead(d)
      sources = [["%s(%s)" % (s.name,l) for l in s.levels] for s in ss]
      for i in product(*sources):
        tail = ",".join(i)
        code.append("%s <-- %s." % (head,tail))
    for n in model.getExo():
      code.append("%s <-- true." % self.makeHead(n))
    return code
  def makeHead(self,var):
    p = 1.0/len(var.levels)
    return ",".join(["%s:%s(%s)" % (p,var.name,l) for l in var.levels])

class TableResultInterpreter:
  def interprete(self,model,results):
    res = {}
    for (nname,n) in model.nodes.items():
      patt = re.compile("([0-9.]*:%s\(\w*\),?)* <-- .*" % nname)
      d = {}
      for (code,prob) in results.items():
        m = patt.match(code)
        if m is not None:
          m2 = re.match("(.*) <-- (.*).",code)
          head = m2.group(1)
          cond = m2.group(2)
          targets = re.findall("%s\((.*?)\)"%nname,head)
          pairedresults = dict(zip(targets,prob))
          d[cond] = pairedresults
      res[nname] = d
    return res