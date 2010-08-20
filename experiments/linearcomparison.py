#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import LinearCPLogicGenerator,MajorityLinearCPLogicGenerator
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer
from semcplogic.dataset import Dataset
from semcplogic.cpmodel import TableResultInterpreter
from experiments.latexreport import LatexTableResultInterpreter

b = ModelBuilder()
b.addNode("a")
b.addNode("b")
b.addNode("c")
b.addNode("d")
b.setInfluence("a","d",1)
b.setInfluence("b","d",1)
b.setInfluence("c","d",1)
m = b.consume()

d = m.sample(200)
d = d.makeDiff()
d = d.discretise()

def runCode(generator):
  cpcode = generator.generate(m)
  cc = CPCompiler()
  runmodel = cc.compileCode(cpcode,d)
  runmodel.iterations = 1000
  result = runmodel.run()
  return result

reslin = runCode(LinearCPLogicGenerator())
resmaj = runCode(MajorityLinearCPLogicGenerator())

print "Gelijke verdeling:"
reslin.printReport()
g = GnuplotDrawer()
g.draw(reslin)
print "Meerderheidsverdeling:"
resmaj.printReport()
g = GnuplotDrawer()
g.draw(resmaj,prefix="maj-")

import tempfile
datafile = tempfile.NamedTemporaryFile()
for p in zip(reslin.sse, resmaj.sse):
  datafile.file.write("\t".join([str(num) for num in p]) + "\n")
datafile.file.flush()
g.callGnuplot(2,datafile.name,"fits.png")
datafile.close()
