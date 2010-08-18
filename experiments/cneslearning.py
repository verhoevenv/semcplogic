#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import NonLinearCPLogicGenerator
from semcplogic import dataset
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer
from semcplogic.cpmodel import TableResultInterpreter
from experiments.latexreport import LatexTableResultInterpreter

def toTwoLevel(var,data):
  newdata = []
  for d in data:
    if d == "stronglyagree":
      newdata.append("agree")
    elif d == "stronglydisagree":
      newdata.append("disagree")
    else:
      newdata.append(d)
  return newdata

b = ModelBuilder()
for var in ["f","mbsa2","mbsa7","mbsa8","mbsa9"]:
  b.addNode(var)
  b.setLevels(var,["Disagree","Agree"])
  #b.setLevels(var,["StronglyDisagree","Disagree","Agree","StronglyAgree"])
b.setInfluence("f","mbsa2",1)
b.setInfluence("f","mbsa7",1)
b.setInfluence("f","mbsa8",1)
b.setInfluence("f","mbsa9",1)
m = b.consume()

data = dataset.fromCSV("experiments/cnesdata.csv")
data = data.discretiseFunc(toTwoLevel)

lincp = NonLinearCPLogicGenerator()
cpcode = lincp.generate(m)

cc = CPCompiler()
runmodel = cc.compileCode(cpcode,data)
runmodel.iterations = 1000
result = runmodel.run()
g = GnuplotDrawer()
g.draw(result)
t = TableResultInterpreter()
r = t.interprete(m,result.latest())
replace = [
  ("f","$F$"),
  ("mbsa2","$MBSA_2$"),
  ("mbsa7","$MBSA_7$"),
  ("mbsa8","$MBSA_8$"),
  ("mbsa9","$MBSA_9$"),
  ]
ltri = LatexTableResultInterpreter(r,replace)
print ltri.out()
