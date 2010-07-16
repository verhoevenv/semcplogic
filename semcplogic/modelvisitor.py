#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

class SampleException(Exception):
  pass

class ModelVisitor:
  def __init__(self,model,startnodes):
    if startnodes == []:
      raise SampleException("Can't sample without a set of starting nodes.")
    self.m = model
    self.startnodes = startnodes
    self.todo = self.tsort()
    for n in self.startnodes:
      self.initNode(n)
      self.todo.remove(n)
  def tsort(self):
    e = [(a.name,b.name) for (a,b) in self.m.getLinks() if not b.name in self.startnodes]
    l = []
    s = list(self.startnodes)
    while s != []:
      n = s.pop()
      l.append(n)
      for m in [y for (x,y) in e if x == n]:
        e.remove((n,m))
        if not any(map(lambda x: x[1] == m,e)):
          s.append(m)
    if e != []:
      raise SampleException("Model has an unbroken cycle!")
    return l
  def start(self):
    for n in self.todo:
      self.visit(n)
    return self.getResult()
    
  #override following in subclasses
  def visit(self,node):
    pass
  def initNode(self,node):
    pass
  def getResult(self):
    return None

class ContinuousSampler(ModelVisitor):
  def __init__(self,model,startnodes):
    self.nodeval = {}
    ModelVisitor.__init__(self,model,startnodes)
  def initNode(self,node):
    avg = self.m.nodes[node].avg
    stddev = self.m.nodes[node].stddev
    self.setAtRandom(node,avg,stddev)
  def setAtRandom(self,node,avg,stddev):
    assert(not self.alreadySampled(node))
    val = random.normalvariate(avg,stddev)
    self.nodeval[node] = val
  def visit(self,node):
    ancs = [x.name for (x,y) in self.m.getLinks() if y.name == node]
    totalinf = 0
    for n in ancs:
      influence = self.m.nodes[n].links[self.m.nodes[node]].influence
      if n is None:
        raise SampleException("Can't sample when parameters are marked for learning!")
      increase = self.nodeval[n] - self.m.nodes[n].avg
      totalinf += influence * increase
    self.setAtRandom(node,self.m.nodes[node].avg + totalinf,self.m.nodes[node].stddev)
  def alreadySampled(self,node):
    return self.nodeval.has_key(node)
  def getResult(self):
    outputnodes = set(self.m.getObservableVariables())
    allnodes = set(self.nodeval.keys())
    assert(allnodes.issuperset(outputnodes))
    latentnodes = allnodes - outputnodes
    for n in latentnodes:
      del self.nodeval[n]
    return self.nodeval
  def sample(self):
    return self.start()

class DiscreteSampler(ModelVisitor):
  #NOTE: not finished, will not work!
  def __init__(self,model,startnodes):
    self.nodeval = {}
    ModelVisitor.__init__(self,model,startnodes)
  def initNode(self,node):
    #Hmm, a priori probability distribution?
    levels = self.m.nodes[node].levels
    self.setAtRandom(node,levels)
  def setAtRandom(self,node,levels):
    assert(not self.alreadySampled(node))
    val = random.choice(levels)
    self.nodeval[node] = val
  def visit(self,node):
    ancs = [x.name for (x,y) in self.m.getLinks() if y.name == node]
    totalinf = 0
    for n in ancs:
      influence = self.m.nodes[n].links[self.m.nodes[node]].influence
      if n is None:
        raise SampleException("Can't sample when parameters are marked for learning!")
      increase = self.nodeval[n] - self.m.nodes[n].avg
      totalinf += influence * increase
    self.setAtRandom(node,self.m.nodes[node].avg + totalinf,self.m.nodes[node].stddev)
  def alreadySampled(self,node):
    return self.nodeval.has_key(node)
  def getResult(self):
    return self.nodeval
  def sample(self):
    return self.start()


import unittest
import model

class ContinuousSamplerTests(unittest.TestCase):
  def testSample(self):
    b = model.ModelBuilder()
    b.addNode("a")
    b.addNode("b",0,0)
    b.setInfluence("a","b",1)
    m = b.consume()
    c = ContinuousSampler(m,"a")
    d = c.sample()
    self.assertTrue(d.has_key("a"))
    self.assertTrue(d.has_key("b"))
    self.assertFalse(d.has_key("c"))
    self.assertAlmostEqual(d["a"],d["b"])
  def testCyclic(self):
    b = model.ModelBuilder()
    b.addNode("a",0)
    b.addNode("b",0,0)
    b.addNode("c",0,0)
    b.setInfluence("a","b",1)
    b.setInfluence("b","c",1)
    b.setInfluence("c","a",1)
    m = b.consume()
    c = ContinuousSampler(m,"a")
    d = c.sample()
    self.assertAlmostEqual(d["a"],d["b"])
    self.assertAlmostEqual(d["a"],d["c"])
    c = ContinuousSampler(m,"b")
    d = c.sample()
    self.assertAlmostEqual(d["b"],d["c"])
    self.assertNotEqual(d["c"],d["a"])
    
if __name__ == '__main__':
  unittest.main()
