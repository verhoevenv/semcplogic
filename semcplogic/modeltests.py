#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from model import *

class ModelBuilderTestCase(unittest.TestCase):
  def testAddNode(self):
    b = ModelBuilder()
    b.addNode("a")
    m = b.consume()
    self.assertTrue("a" in m.nodes)
    self.assertFalse("b" in m.nodes)
  def testRemoveNode(self):
    b = ModelBuilder()
    b.addNode("a")
    b.addNode("b")
    b.addNode("c")
    b.setInfluence("a","b",1)
    b.setInfluence("b","c",1)
    b.removeNode("c")
    m = b.consume()
    self.assertTrue("a" in m.nodes)
    self.assertTrue("b" in m.nodes)
    self.assertFalse("c" in m.nodes)
    self.assertEquals(("a","b"),tuple(map(lambda x: x.name,m.getLinks()[0])))
    self.assertEquals(1,len(m.getLinks()))

if __name__ == '__main__':
  unittest.main()
