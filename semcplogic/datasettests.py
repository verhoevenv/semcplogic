#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from dataset import *

class TransposeTestCase(unittest.TestCase):
  def testTranspose(self):
    m = [[1,2,3],[4,5,6]]
    m2 = transpose(m)
    self.assertEqual(m[0][1],2)
    self.assertEqual(m2[1][0],2)
    self.assertEqual(m[1][2],6)
    self.assertEqual(m2[2][1],6)

class DiscretiseTestCase(unittest.TestCase):
  def testTwoLevel(self):
    v = [3,2,1,4]
    d = discretise(v)
    self.assertEqual(d,["hoog","laag","laag","hoog"])
  def testOddNumber(self):
    v = [3,2,1,4,5]
    d = discretise(v)
    self.assertEqual(d,["hoog","laag","laag","hoog","hoog"])
  def testMultilevel(self):
    v = [3,2,1,4,5]
    d = discretise(v,["laag","middel","hoog"])
    self.assertEqual(d,["middel","middel","laag","hoog","hoog"])
  def testMultilevel2(self):
    v = [3,2,1,4,5]
    d = discretise(v,[1,2,3,4,5])
    self.assertEqual(d,[3,2,1,4,5])
    
class DatasetTestCase(unittest.TestCase):
  def testDiff(self):
    d = Dataset(["a"])
    d.addData([7])
    d.addData([8])
    d.addData([9])
    d.addData([10])
    diff = d.makeDiff()
    self.assertTrue([1] in diff.data)
    self.assertTrue([2] in diff.data)
    self.assertTrue([3] in diff.data)
    self.assertFalse([0] in diff.data)
    self.assertFalse([4] in diff.data)
    self.assertFalse([10] in diff.data)
    self.assertEqual(len(diff.data),6)
  def testDiscretise(self):
    d = Dataset(["a","b"])
    d.addData([7,2.3])
    d.addData([8,5.1])
    d.addData([9,1.6])
    d.addData([10,7.9])
    disc = d.discretise()
    self.assertEqual(disc.data,[["laag","laag"],["laag","hoog"],["hoog","laag"],["hoog","hoog"]])

if __name__ == '__main__':
  unittest.main()
