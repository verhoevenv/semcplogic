#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.dataset import Dataset
from semcplogic.cpcompiler import CPCompiler, ProblogExample
from semcplogic.problogresult import GnuplotDrawer
import pprint

#using t(1) constrains this paramter to 1 - the sum of the other parameters
cpcode = ["t(_): nothing, t(_) : a, t(1): b <-- true."]

cc = CPCompiler()

data = []
data.append(ProblogExample(0,"a",weight=0.1))
data.append(ProblogExample(1,"b",weight=0.4))
data.append(ProblogExample(2,"nothing",weight=0.5))
cc.weight=False

runmodel = cc.compileCode(cpcode,otherexamples=data)
runmodel.iterations = 100
result = runmodel.run()
pprint.pprint(result.probs[-1])

#Check each iteration and see if the sum of parameters is indeed (about) 1.
params = [x.values()[0] for x in result.probs]
assert(all((abs(1 - sum(x)) < 1e-6) for x in params))
