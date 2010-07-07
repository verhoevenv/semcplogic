#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
from dataset import Dataset
from modelvisitor import ContinuousSampler

class Node:
  def __init__(self,name,avg=0.0,stddev=1.0):
    self.name = name
    self.links = {} #Node -> Influence
    self.ancs = {} #Node -> Influence
    self.avg = float(avg)
    self.stddev = float(stddev)
    self.exo = True
    self.levels = ["laag","hoog"]
  def __str__(self):
    return "%s (%s,%s)" % (self.name,self.avg,self.stddev)
  def influences(self,n,s):
    i = Influence(self,n,influence=s)
    self.links[n] = i
    n.ancs[self] = i
    if s == 0:
      del self.links[n]
      del n.ancs[self]
  def markChildren(self):
    for child in self.links.keys():
      child.exo = False
  def setLevels(self,levels):
    self.levels = levels
    for i in self.links.values():
      i.levelChanged()
    for i in self.ancs.values():
      i.levelChanged()

class Influence:
  def __init__(self,start,end,influence=1.0,trans=None):
    self.start = start
    self.end = end
    self.influence = influence
    self.trans = trans
    if trans is None:
      self.trans = [None] * len(start.levels)
  def levelChanged(self):
    while len(self.trans) < len(self.start.levels):
      self.trans.append(None)
    while len(self.trans) > len(self.start.levels):
      del self.trans[-1]
    for row in self.trans:
      if not row is None:
        while len(self.trans) < len(self.start.levels):
          row.append(0)
        while len(self.trans) > len(self.start.levels):
          del row[-1]
  def setIdentityTrans(self):
    for i in len(self.trans):
      for j in len(self.trans[i]):
        if i == j:
          self.trans[i][j] = 1
        else:
          self.trans[i][j] = 0

class Model:
  def __init__(self,nodes=[]):
    self.nodes = dict([(n.name,n) for n in nodes])
    self.analysed = False
  def clone(self):
    return copy.deepcopy(self)
  def analyse(self):
    ns = self.nodes.values()
    for n in ns:
      n.exo = True
    for n in ns:
      n.markChildren()
    self.analysed = True
  def sample(self,n):
    assert(self.analysed)
    startnodes = [node.name for node in self.nodes.values() if node.exo]
    return self.sampleNodes(n,startnodes)
  def sampleNodes(self,n,startnodes):
    d = Dataset(self.nodes.keys())
    for i in xrange(n):
      d.addDictData(self.sampleOnce(startnodes))
    return d
  def sampleOnce(self,startnodes):
    s = ContinuousSampler(self,startnodes)
    return s.sample()
  def getLinks(self):
    links = []
    for n in self.nodes.values():
      links.extend([(n,l) for l in n.links.keys()])
    return links
  def getExo(self):
    return [n for n in self.nodes.values() if n.exo]
  def getLevels(self):
    return dict([(n.name,n.levels) for n in self.nodes.values()])

class ModelBuilder:
  def __init__(self):
    self.ns = {}
    self.consumed = False
  def addNode(self,name,avg=0,stddev=1):
    n = Node(name,avg,stddev)
    self.ns[name] = n
  def setInfluence(self,fromNode,toNode,amount):
    self.ns[fromNode].influences(self.ns[toNode],amount)
  def setName(self,oldname,newname):
    n = self.ns[oldname]
    del self.ns[oldname]
    n.name = newname
    self.ns[newname] = n
  def setAvg(self,node,avg):
    self.ns[node].avg = avg
  def setStddev(self,node,stddev):
    self.ns[node].stddev = stddev
  def setLevels(self,node,levels):
    self.ns[node].setLevels(levels)
  def removeNode(self,name):
    for n in self.ns.keys():
      self.setInfluence(n,name,0)
    del self.ns[name]
  def canConsume(self):
    return not self.consumed
  def consume(self):
    assert(self.canConsume())
    self.consumed = True
    m = Model(self.ns.values())
    m.analyse()
    return m

class ContinuousModelBuilder(ModelBuilder):
  """Like ModelBuilder, but does not test for single usage."""
  def __init__(self):
    ModelBuilder.__init__(self)
  def canConsume(self):
    return True
