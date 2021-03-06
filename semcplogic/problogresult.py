#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import os
from collections import defaultdict
import re
import tempfile
import subprocess
import itertools

import config

def createcmp(filename):
  def probcmp(x,y):
    m1 = re.match("%s_(\d+).pl"%filename,x)
    numx = int(m1.group(1))
    m2 = re.match("%s_(\d+).pl"%filename,y)
    numy = int(m2.group(1))
    return cmp(numx,numy)
  return probcmp

def paramAgg(l,d):
  m = re.match("(\S+) :: (\S+).",l)
  d[m.group(2)] = float(m.group(1))

def errorAgg(l,d):
  m = re.match("ex\((\d+),(train|test),(\d+),([a-zA-Z\(\)0-9_,]+),([\d.]+),([\d.]+)\).",l)
  if not m is None:
    abse = abs(float(m.group(5)) - float(m.group(6)))
    d[m.group(3)].append(abse)

class ProblogResult:
  def __init__(self,outputdir,links):
    assert(os.path.isdir(outputdir))
    self.outputdir = outputdir
    self.links = links
    self.gatherResults()
    self.gatherErrors()
    self.calcSSE()
  def gatherResults(self):
    files = self.listFiles("factprobs")
    l = []
    for p in files:
      f = open(os.path.join(self.outputdir,p))
      d = defaultdict(itertools.repeat(1).next)
      for line in f.readlines():
        paramAgg(line,d)
      f.close()
      cpd = self.recalcCPValues(d)
      l.append(cpd)
    self.probs = l
    self.numparams = sum(map(len,l[0].values()))
  def gatherErrors(self):
    files = self.listFiles("predictions")
    l = []
    for p in files:
      f = open(os.path.join(self.outputdir,p))
      d = defaultdict(list)
      for line in f.readlines():
        errorAgg(line,d)
      f.close()
      l.append(d)
    self.errors = l
  def listFiles(self,filename):
    files = os.listdir(self.outputdir)
    l = [f for f in files if re.match("%s_\d+.pl"%filename, f)]
    l.sort(createcmp(filename))
    return l
  def recalcCPValues(self,problogvals):
    newd = {}
    for (k,v) in self.links.items():
      newv = []
      acc = 1
      for var in v:
        val = problogvals[var]
        newv.append(val*acc)
        acc = acc * (1 - val)
      newd[k] = newv
    return newd
  def latest(self):
    return self.probs[-1]
  def calcSSE(self):
    f = []
    for it in self.errors:
      sse = sum([e*e for [e] in it.values()])
      f.append(sse)
    self.sse = f
  def printReport(self):
    import pprint
    print "Probabilities:"
    pprint.pprint(self.latest())
    print "Errors:"
    pprint.pprint(self.errors[-1])
    print "SSE: %s" % self.sse[-1]

class GnuplotDrawer:
  def __init__(self):
    pass
  def draw(self,result,prefix=""):
    self.writeList(result.probs,"%sout.png" % prefix)
    self.writeList(result.errors,"%serror.png" % prefix)
  def writeList(self,l,imgfile):
    datafile = tempfile.NamedTemporaryFile()
    self.writeValues(l,datafile.file)
    numvars = sum(map(len,l[0].values()))
    self.callGnuplot(numvars,datafile.name,imgfile)
    datafile.close()
  def writeValues(self,l,dest):
    for d in l:
      l = [str(f) for k,v in sorted(d.items()) for f in v]
      dest.write("\t".join(l) + "\n")
    dest.flush()
  def callGnuplot(self,numvars,datafile,outfile):
    f = tempfile.NamedTemporaryFile()
    f.file.write("""set term png
    set output "%s"
    set nokey
    """ % outfile)
    ss = []
    for i in range(1,numvars + 1):
      ss.append("\"%s\" using %s" % (datafile,i))
    s = "plot " + ", ".join(ss)
    f.file.write(s + "\n")
    f.file.flush()
    source = os.path.join(tempfile.gettempdir(),f.name)
    subprocess.check_call(["%s %s" % (config.gnuplotcommand,source)],shell=True)
    f.close()
