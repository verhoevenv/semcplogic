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

class ProblogResult:
  def __init__(self,outputdir,links):
    assert(os.path.isdir(outputdir))
    self.outputdir = outputdir
    self.links = links
    self.gatherResults()
  def gatherResults(self):
    files = self.listFiles("factprobs")
    self.probs  = self.globLines(files,paramAgg)
  def listFiles(self,filename):
    files = os.listdir(self.outputdir)
    l = [f for f in files if re.match("%s_\d+.pl"%filename, f)]
    l.sort(createcmp(filename))
    return l
  def globLines(self,probs,aggregatefunc):
    l = []
    for p in probs:
      f = open(os.path.join(self.outputdir,p))
      d = defaultdict(itertools.repeat(1).next)
      for line in f.readlines():
        aggregatefunc(line,d)
      f.close()
      cpd = self.recalcCPValues(d)
      l.append(cpd)
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

class GnuplotDrawer:
  def __init__(self):
    pass
  def draw(self,result):
    datafile = tempfile.NamedTemporaryFile()
    self.writeValues(result.probs,datafile.file)
    self.callGnuplot(result.probs,datafile.name,"out.png")
    datafile.close()
  def writeValues(self,l,dest):
    for d in l:
      l = [str(f) for k,v in sorted(d.items()) for f in v]
      dest.write("\t".join(l) + "\n")
    dest.flush()
  def callGnuplot(self,l,datafile,outfile):
    f = tempfile.NamedTemporaryFile()
    f.file.write("""set term png
    set output "%s"
    set nokey
    """ % outfile)
    ss = []
    for i in range(1,sum(map(len,l[0].values())) + 1):
      ss.append("\"%s\" using %s" % (datafile,i))
    s = "plot " + ", ".join(ss)
    f.file.write(s + "\n")
    f.file.flush()
    source = os.path.join(tempfile.gettempdir(),f.name)
    subprocess.check_call(["%s %s" % (config.gnuplotcommand,source)],shell=True)
    f.close()
