#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
from semcplogic import model
from semcplogic.model import ModelBuilder
from semcplogic.cpmodel import LinearCPLogicGenerator,TableResultInterpreter
from semcplogic.cpcompiler import CPCompiler
from semcplogic.problogresult import GnuplotDrawer
import pprint

def doLearn(model,data):
  cm = LinearCPLogicGenerator()
  cpcode = cm.generate(model)

  cc = CPCompiler()
  runmodel = cc.compileCode(cpcode,data)
  runmodel.iterations = 500
  return runmodel.run()

b = model.ModelBuilder()
b.addNode("a",0,1)
b.addNode("b",0,1)
b.addNode("c",0,1)
b.setInfluence("a","b",1)
b.setInfluence("b","c",1)
#note, no direct influence from a to c
mnull = b.consume()

b = model.ModelBuilder()
b.addNode("a",0,1)
b.addNode("b",0,1)
b.addNode("c",0,1)
b.setInfluence("a","b",1)
b.setInfluence("b","c",1)
b.setInfluence("a","c",1)
minfluence = b.consume()

dnull = mnull.sample(100)
dnull = dnull.makeDiff()
dnull = dnull.discretise()

dinf = minfluence.sample(100)
dinf = dinf.makeDiff()
dinf = dinf.discretise()

resinfnull = doLearn(minfluence,dnull)
resnullnull = doLearn(mnull,dnull)
resinfinf = doLearn(minfluence,dinf)
resnullinf = doLearn(mnull,dinf)
print "IM,ND"
pprint.pprint(resinfnull.fits[-1])
pprint.pprint(resinfnull.latest())
print "NM,ND"
pprint.pprint(resnullnull.fits[-1])
pprint.pprint(resnullnull.latest())
print "IM,ID"
pprint.pprint(resinfinf.fits[-1])
pprint.pprint(resinfinf.latest())
print "NM,ID"
pprint.pprint(resnullinf.fits[-1])
pprint.pprint(resnullinf.latest())
