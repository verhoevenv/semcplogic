#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import NonLinearCPLogicGenerator
from semcplogic import dataset
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer
from semcplogic.cpmodel import TableResultInterpreter
from experiments.latexreport import LatexTableResultInterpreter

b = ModelBuilder()
for var in ["c","p","wp","i","klag","x","wg","plag","xlag","a"]:
    b.addNode(var)
b.setInfluence("xlag","wp",1)
b.setInfluence("x","wp",1)
b.setInfluence("a","wp",1)
b.setInfluence("klag","i",1)
b.setInfluence("plag","i",1)
b.setInfluence("p","i",1)
b.setInfluence("plag","c",1)
b.setInfluence("p","c",1)
b.setInfluence("wg","c",1)
b.setInfluence("wp","c",1)
m = b.consume()

data = dataset.fromCSV("experiments/kleindata.csv")
data = data.makeDiff()
data = data.discretise()

lincp = NonLinearCPLogicGenerator()
cpcode = lincp.generate(m)

cc = CPCompiler()
runmodel = cc.compileCode(cpcode,data)
runmodel.iterations = 10000
result = runmodel.run()
g = GnuplotDrawer()
g.draw(result)
t = TableResultInterpreter()
r = t.interprete(m,result.latest())
ltri = LatexTableResultInterpreter(r)
print ltri.out()
