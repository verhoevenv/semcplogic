#!/usr/bin/python
# -*- coding: utf-8 -*-

from itertools import product,repeat
from collections import defaultdict
import re

def makeHead(var):
  headterms = ["t(_):%s(%s)" % (var.name,l) for l in var.levels]
  headterms[-1] = headterms[-1].replace("t(_)","t(1)")
  return ",".join(headterms)
  
class NonLinearCPLogicGenerator:
  def generate(self,model):
    code = []
    links = model.getLinks()
    linksdict = defaultdict(list)
    for (s,d) in links:
      linksdict[d].append(s)
    for (d,ss) in linksdict.items():
      head = makeHead(d)
      sources = [["%s(%s)" % (s.name,l) for l in s.levels] for s in ss]
      for i in product(*sources):
        tail = ",".join(i)
        code.append("%s <-- %s." % (head,tail))
    for n in model.getExo():
      code.append("%s <-- true." % makeHead(n))
    return code

class TableResultInterpreter:
  def interprete(self,model,results):
    res = {}
    for (nname,n) in model.nodes.items():
      patt = re.compile("(t\([1_]\):%s\(\w*\),?)* <-- .*" % nname)
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

class LinearCPLogicGenerator:
  def generate(self,model):
    code = []
    for n in model.nodes.values():
      ancs = n.ancs.keys()
      assert all(a.levels == n.levels for a in ancs),"Levels should be equal for the linear model!"
      for anc in ancs:
        for level in anc.levels:
          headterms = ["t(_):%s_vote_%s(%s)" % (n.name,anc.name,l) for l in n.levels]
          headterms[-1] = headterms[-1].replace("t(_)","t(1)")
          head = ",".join(headterms)
          body = "%s(%s)" % (anc.name,level)
          code.append("%s <-- %s." % (head,body))
      
      sources = [[(a.name,l) for l in a.levels] for a in ancs]
      if ancs == []:
        code.append("%s <-- true." % makeHead(n))
      else:
        for i in product(*sources):
          d = defaultdict(int)
          for (_,level) in i:
            d[level] += 1
          head = self.makeVoteHead(d,len(ancs),n.name)
          bodyterms = ["%s_vote_%s(%s)" % (n.name,name,level) for (name,level) in i]
          body = ",".join(bodyterms)
          code.append("%s <-- %s." % (head,body))
    return code
  def makeVoteHead(self,levelcounts,totallevels,name):
     headterms = ["%s:%s(%s)" % (float(count)/totallevels,name,level) for (level,count) in levelcounts.items()]
     return ",".join(headterms)

class MajorityLinearCPLogicGenerator(LinearCPLogicGenerator):
  def makeVoteHead(self,levelcounts,totallevels,name):
    major = max(levelcounts.values())
    #distribute it evenly in case there is a tie
    levels = [level for (level,count) in levelcounts.items() if count==major]
    return ",".join(["%s:%s(%s)" % (1/len(levels),name,level) for level in levels])
