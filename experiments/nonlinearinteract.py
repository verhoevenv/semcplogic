#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import NonLinearCPLogicGenerator,LinearCPLogicGenerator
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer
from semcplogic.dataset import Dataset
from semcplogic.cpmodel import TableResultInterpreter
from experiments.latexreport import LatexTableResultInterpreter

b = ModelBuilder()
b.addNode("a")
b.addNode("b")
b.addNode("c")
b.setInfluence("a","c",1)
b.setInfluence("b","c",1)
m = b.consume()

d = Dataset(["a","b","c"])
d.addData(["laag","laag","hoog"])
d.addData(["laag","hoog","laag"])
d.addData(["hoog","laag","laag"])
d.addData(["hoog","hoog","hoog"])

def runCode(generator):
  cpcode = generator.generate(m)
  cc = CPCompiler()
  runmodel = cc.compileCode(cpcode,d)
  runmodel.iterations = 1000
  result = runmodel.run()
  return result

resnonlin = runCode(NonLinearCPLogicGenerator())
reslin = runCode(LinearCPLogicGenerator())

print "Niet-lineair:"
resnonlin.printReport()
g = GnuplotDrawer()
g.draw(resnonlin)
t = TableResultInterpreter()
r = t.interprete(m,resnonlin.latest())
ltri = LatexTableResultInterpreter(r)
print ltri.out()
print "Lineair:"
reslin.printReport()
g = GnuplotDrawer()
g.draw(reslin,prefix="lin-")
