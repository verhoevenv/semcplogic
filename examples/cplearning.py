#!/usr/bin/python
# -*- coding: utf-8 -*-

from semcplogic.dataset import Dataset
from semcplogic.cpmodel import TableResultInterpreter
from semcplogic.cpcompiler import CPCompiler, ProblogExample
from semcplogic.problogresult import GnuplotDrawer
import pprint

#We use "breaks" because break is a reserved keyword in problog
#We add the probabilities here, but they get removed on compiling
cpcode = """0.8 : breaks <-- throws(mary).
0.6 : breaks <-- throws(john).
0.5 : throws(mary) <-- true.
1 : throws(john) <-- true.
""".split("\n")

cc = CPCompiler()

data = []
#Two ideas that don't work
#i = 0
#for i in xrange(i+1,i+1+23):
#  data.append(ProblogExample(i,"throws(mary),throws(john),breaks"))
#for i in xrange(i+1,i+1+2):
#  data.append(ProblogExample(i,"throws(mary),throws(john)"))
#for i in xrange(i+1,i+1+15):
#  data.append(ProblogExample(i,"throws(john),breaks"))
#for i in xrange(i+1,i+1+10):
#  data.append(ProblogExample(i,"throws(john)"))

#i = 0
#for i in xrange(i+1,i+1+23):
#  data.append(ProblogExample(i,"throws(mary),throws(john),breaks"))
#for i in xrange(i+1,i+1+2):
#  data.append(ProblogExample(i,"throws(mary),throws(john),problog_not(breaks)"))
#for i in xrange(i+1,i+1+15):
#  data.append(ProblogExample(i,"problog_not(throws_mary),throws(john),breaks"))
#for i in xrange(i+1,i+1+10):
#  data.append(ProblogExample(i,"problog_not(throws_mary),throws(john),problog_not(breaks)"))

#To make it work, be sure the proofs only contain positive information
#if necessary, marginalize variables
data.append(ProblogExample(0,"breaks",weight=0.76))
data.append(ProblogExample(1,"throws(mary)",weight=0.5))
data.append(ProblogExample(2,"throws(john)",weight=1))
data.append(ProblogExample(3,"throws(john),throws(mary),breaks",weight=0.46))
#We give the weights, so don't calculate them
cc.weight=False

runmodel = cc.compileCode(cpcode,otherexamples=data)
runmodel.iterations = 100
result = runmodel.run()
g = GnuplotDrawer()
g.draw(result)
pprint.pprint(result.probs[-1])
