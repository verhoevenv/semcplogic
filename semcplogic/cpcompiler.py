#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os.path
import re
import random
from collections import defaultdict
import tempfile

import config
from problogresult import ProblogResult

class ProblogExample:
  def __init__(self,idx,proof,exampletype="example",weight=1.0):
    self.exampletype = exampletype
    self.idx = idx
    self.proof = proof
    self.weight = weight
  def __str__(self):
    return "%s(%s,(%s),%s)." % (self.exampletype,self.idx,self.proof,self.weight)

class RunnableProblogModel:
  def __init__(self,code,linkmodel):
    self.code = code
    self.links = linkmodel
    self.iterations = 20
  def getOutputDir(self):
    return os.path.join(tempfile.gettempdir(),"output")
  def run(self):
    try:
      modelsource = tempfile.NamedTemporaryFile(suffix=".pl")
      modelsource.file.write("\n".join(self.code))
      modelsource.file.flush()
      callfile = tempfile.NamedTemporaryFile(suffix=".pl")
      contents = ":- ['%s'].\n:- do_learning(%s)." % (modelsource.name,self.iterations)
      callfile.file.write(contents)
      callfile.file.flush()
      #TODO: gather the text output (progress) from the subprocess and somehow show it
      #This doesn't seem easily doable (cfr PEP 3145)
      subprocess.check_call([os.path.expanduser(config.yapcommand), "-L", callfile.name])
      return ProblogResult(self.getOutputDir(),self.links)
    finally:
      modelsource.close()
      callfile.close()

#This class is very simplistic
#in case the compiler changes, this might cause trouble!
class CPProblogLink:
  def __init__(self,cpcode,problogcode):
    self.matchvars(cpcode,problogcode)

  def matchvars(self,cpcode,problogcode):
    cpcode = self.cleanSource(cpcode)
    problogcode = self.cleanSource(problogcode)
    #skip import line
    problogcode = problogcode[1:]
    self.vardict = self.getVars(cpcode,problogcode)

  def cleanSource(self,code):
    code = [x for x in code if not x == ""]
    code = [x for x in code if not x[0] == "%"]
    return code

  def countLevels(self,sourceline):
    return sourceline.count(":")

  def getVars(self,cp,problog):
    d = defaultdict(list)
    for line in cp:
      levels = self.countLevels(line)
      #1 line definition with probability + 1 line prolog rule
      #we need at least these lines to continue
      assert(len(problog) >= levels * 2)
      #get var definitions
      clines = problog[:levels]
      #remove definitions and rules
      problog = problog[levels*2:]
      if "t(_)" in line:
        for cline in clines:
          m = re.match("(\d\.\d{6}::)?([\w\(\)]*).",cline)
          if m:
            var = m.group(2)
            d[line].append(var)
    assert(len(problog) == 0 or "example" in problog[0])
    return d
    
  def hasVar(self,problogvar):
    return any((problogvar in x) for x in self.vardict.values())

class CPCompiler:
  def __init__(self):
    self.learning = True
    self.validationpercent = 0
    self.weight = True

  def compileCode(self,cpcode,data=None,otherexamples=None):
    alteredcpcode = self.replaceLearningParameters(cpcode)
    lines = self.cpToProblog(alteredcpcode)
    lines = self.cleanProblog(lines)
    if data is not None:
      lines.extend(self.makeExamples(data))
    if otherexamples is not None:
      lines.extend(self.makeExampleCode(otherexamples))
    link = CPProblogLink(cpcode,lines)
    newlines = []
    for line in lines:
      m = re.match("(\d\.\d{6}::)?([\w\(\)]*).",line)
      if m:
        var = m.group(2)
        if link.hasVar(var):
          newlines.append(re.sub("\d\.\d{6}::","t(_)::",line))
        else:
          newlines.append(line)
    return RunnableProblogModel(newlines,link.vardict)

  def replaceLearningParameters(self,code):
    return [re.sub("t\(\_\)","0.1",line) for line in code]

  def cpToProblog(self,cpcode):
    try:
      filein = tempfile.NamedTemporaryFile()
      filein.write("\n".join(cpcode))
      #filein.close()
      filein.file.flush()
      fileout = tempfile.NamedTemporaryFile()
      compilerfile = "%s/cplogic.pl" % os.path.expanduser(config.cplcompilerpath)
      subprocess.check_call([os.path.expanduser(config.yapcommand), "-L", compilerfile, "--", filein.name, fileout.name])
      return fileout.file.read().splitlines()
    finally:
      filein.close()
      fileout.close()

  def cleanProblog(self,lines):
    #change module location
    problog = os.path.expanduser(config.problogpath)
    if self.learning:
      module = "learning"
    else:
      module = "problog"
    modulelocation = os.path.join(os.path.abspath(problog),module)
    lines[0] = ":- use_module('%s')."%modulelocation
    #remove probabilistic information for P=1
    #it only causes the BDD tool to get confused
    lines = [re.sub("1.000000::","",x) for x in lines]
    return lines

  def makeExamples(self,dataset):
    #add examples, select random test_examples
    examples = []
    for (i,row) in enumerate(dataset.getData()):
      proof = "true"
      for (k,v) in zip(dataset.getVariables(),row):
        proof += ",%s(%s)" % (k,v)
      examples.append(ProblogExample(i,proof,"example",1.0))
    return self.makeExampleCode(examples)
  
  def makeExampleCode(self,examples):
    (examples,validation) = self.selectValidation(examples)
    if self.weight:
      examples = self.gatherWeights(examples)
      validation = self.gatherWeights(validation)
    excode = []
    excode.extend([str(x) for x in examples])
    excode.extend([str(x) for x in validation])
    return excode
    

  def gatherWeights(self,data):
    numoccurs = defaultdict(int)
    datapoints = 0
    for d in data:
      numoccurs[d.proof] += 1
      d.toRemove = (numoccurs[d.proof] > 1)
      datapoints += 1
    for d in data:
      d.weight = float(numoccurs[d.proof])/datapoints
    return [d for d in data if not d.toRemove]

  def selectValidation(self,examples):
    numval = len(examples)*self.validationpercent/100
    tests = random.sample(range(len(examples)),numval)
    tests.sort()
    tests.reverse()
    validation = []
    for i in tests:
      validation.append(examples[i])
      validation[-1].exampletype = "test_example"
      del examples[i]
    validation.reverse()
    return (examples,validation)
