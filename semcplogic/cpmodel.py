#!/usr/bin/python
# -*- coding: utf-8 -*-

from itertools import product
from collections import defaultdict

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
