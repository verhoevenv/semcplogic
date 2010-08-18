#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.cpmodel import TableResultInterpreter

head = """\\begin{figure}
\\centering
"""

foot = """\\caption{}
\\label{tbl:}
\\end{figure}
"""

tblhead = """\\subtable{
\\begin{tabular}{l|%s}
"""
tblfoot = """\\end{tabular}
}\hspace{-1mm}
"""

class LatexTableResultInterpreter:
  def __init__(self,tableres,subst=[]):
    self.res = tableres
    self.subst = subst
  def out(self):
    output = head
    for (var,dic) in self.res.items():
      output += self.dovar(var,dic)
      output += "\n"
    output += foot
    for (f,t) in self.subst:
      output = output.replace(f,t)
    return output
  def dovar(self,var,dic):
    lvls = dic.values()[0]
    numlvls = len(lvls)
    out = ""
    out += tblhead % ("r"*numlvls,)
    out += " & %s \\\\\n" % (" & ".join(["%s(%s)" % (var,l) for l in lvls]),)
    out += "\\hline\n"
    for (cond,params) in dic.items():
      out += "%s & " % (cond,)
      out += " & ".join([str(params[lvl]) for lvl in lvls])
      out += "\\\\\n"
    out += tblfoot
    return out
