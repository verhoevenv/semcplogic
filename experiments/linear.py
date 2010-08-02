#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import LinearCPLogicGenerator
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer
import pprint
from collections import defaultdict
from itertools import repeat

b = ModelBuilder()
b.addNode("a")
b.addNode("b")
b.addNode("c")
b.addNode("d")
b.setInfluence("a","d",1)
b.setInfluence("b","d",1)
b.setInfluence("c","d",1)
m = b.consume()

d = m.sample(100)
d2 = d.discretise(defaultdict(repeat(["laag","hoog"]).next))

lincp = LinearCPLogicGenerator()
cpcode = lincp.generate(m)
pprint.pprint(cpcode)

cc = CPCompiler()
runmodel = cc.compileCode(cpcode,d2)
runmodel.iterations = 1
result = runmodel.run()
g = GnuplotDrawer()
g.draw(result)
pprint.pprint(result.probs[-1])
