#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
from semcplogic import model

b = model.ModelBuilder()
b.addNode("v1",0,1)
b.addNode("v2",0,1)
b.addNode("v3",0,1)
b.addNode("f",0,0)
b.setInfluence("v1","f",1)
b.setInfluence("v2","f",1)
b.setInfluence("v3","f",1)
m = b.consume()

#print sampleOnce([f,v1,v2,v3,v4])

w = csv.DictWriter(open("raw.csv","w"),["f","v1","v2","v3"])
w.writerow({"f":"f","v1":"v1","v2":"v2","v3":"v3"})
for i in xrange(10000):
  w.writerow(m.sampleOnce(["v1","v2","v3"]))
