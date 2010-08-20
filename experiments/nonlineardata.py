#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import NonLinearCPLogicGenerator,LinearCPLogicGenerator
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer
from semcplogic.dataset import Dataset

b = ModelBuilder()
b.addNode("a")
b.addNode("b")
b.setInfluence("a","b",1)
m = b.consume()

levels = ["l1","l2","l3","l4","l5"]

m.nodes["a"].setLevels(levels)
m.nodes["b"].setLevels(levels)
d = m.sample(200)
newdata = [[a,b - a + a*a] for [a,b] in d.data]
d2 = Dataset(["a","b"])
for p in newdata:
  d2.addData(p)
d2 = d2.makeDiff()
d2 = d2.discretise({"a":levels,"b":levels})

def runCode(generator):
  cpcode = generator.generate(m)
  cc = CPCompiler()
  runmodel = cc.compileCode(cpcode,d2)
  runmodel.iterations = 500
  result = runmodel.run()
  return result

resnonlin = runCode(NonLinearCPLogicGenerator())
reslin = runCode(LinearCPLogicGenerator())

print "Niet-lineair:"
resnonlin.printReport()
g = GnuplotDrawer()
g.draw(resnonlin)
print "Lineair:"
reslin.printReport()
g = GnuplotDrawer()
g.draw(reslin,prefix="lin-")
