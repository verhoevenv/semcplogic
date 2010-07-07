#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import CPLogicGenerator
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer

b = ModelBuilder()
b.addNode("f")
b.addNode("v1",0,1)
b.addNode("v2",0,1)
b.setInfluence("f","v1",5)
b.setInfluence("f","v2",5)
m = b.consume()

d = m.sample(100,["v1","v2"])
d2 = d.discretise({"v1":["hoog","laag"],"v2":["hoog","laag"]})

cm = CPLogicGenerator()
cpcode = cm.generate(m)

cc = CPCompiler()
runmodel = cc.compileCode(cpcode,d2)
runmodel.iterations = 250
result = runmodel.run()
import pprint; pprint.pprint(result.probs)
g = GnuplotDrawer()
g.draw(result)
