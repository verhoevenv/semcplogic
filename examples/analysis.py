#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import NonLinearCPLogicGenerator,TableResultInterpreter
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer
import pprint

b = ModelBuilder()
b.addNode("a")
b.addNode("b",0,0)
b.addNode("c",0,0)
b.setInfluence("a","b",5)
b.setInfluence("a","c",5)
m = b.consume()

m.nodes["c"].setLevels(["laag","middel","hoog"])
d = m.sample(100)
d2 = d.discretise({"a":["laag","hoog"],"b":["laag","hoog"],"c":["laag","middel","hoog"]})

cm = NonLinearCPLogicGenerator()
cpcode = cm.generate(m)

cc = CPCompiler()
runmodel = cc.compileCode(cpcode,d2)
runmodel.iterations = 100
result = runmodel.run()
g = GnuplotDrawer()
g.draw(result)
t = TableResultInterpreter()
r = t.interprete(m,result.latest())
pprint.pprint(r)
