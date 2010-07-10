#!/usr/bin/python
# -*- coding: utf-8 -*-

import operator
import csv
from collections import defaultdict
from itertools import repeat

def transpose(matrix):
  m = [[0 for _ in xrange(len(matrix))] for _ in xrange(len(matrix[0]))]
  for (i,row) in enumerate(matrix):
    for (j,elem) in enumerate(row):
      m[j][i] = elem
  return m

def discretise(vector,levels=["laag","hoog"]):
  """Partitions the data in approximately equally large sets. Probably not in a statistically valid way.
  levels is a list with the lowest discretisation level first."""
  l = len(vector)
  s = sorted(vector)
  elemspersub = float(l)/len(levels)
  elems = []
  for i in xrange(len(levels)):
    elems.append(s[int(elemspersub*i)])
  discretised = []
  for e in vector:
    level = 0
    while level < len(levels) - 1 and e >= elems[level + 1]:
      level += 1
    discretised.append(levels[level])
  return discretised

class Dataset:
  def __init__(self,variables):
    self.data = []
    self.variables = list(variables)
  def __len__(self):
    return len(self.data)
  def addDictData(self,data):
    assert(len(data) == len(self.variables))
    self.data.append([data[x] for x in self.variables])
  def addData(self,point):
    assert(len(point) == len(self.variables))
    self.data.append(list(point))
  def getData(self):
    return self.data
  def asDict(self):
    return [self.pointAsDict(p) for p in xrange(len(self.data))]
  def pointAsDict(self,index):
    datum = self.data[index]
    return dict(zip(self.variables,datum))
  def getVariables(self):
    return self.variables
  def makeDiff(self):
    d = Dataset(self.variables)
    for i in xrange(len(self.data) - 1):
      for j in xrange(i+1,len(self.data)):
        d.addData(map(operator.sub,self.data[j],self.data[i]))
    return d
  def discretise(self,levels=defaultdict(repeat(["laag","hoog"]).next)):
    d = Dataset(self.variables)
    t = transpose(self.data)
    tdisc = [discretise(data,levels[var]) for (var,data) in zip(self.variables,t)]
    dnew = transpose(tdisc)
    for e in dnew:
      d.addData(e)
    return d

def fromCSV(path):
  r = csv.DictReader(open(path))
  d = Dataset(r.fieldnames)
  for row in r:
    d.addDictData(row)
  return d
