# -*- coding: utf-8 -*-
from Tkinter import *
import tkFileDialog
import tkSimpleDialog
import pickle
from math import sqrt

from ..model import Model,ContinuousModelBuilder

class GuiModel:
  def __init__(self,canvas):
    self.canvas = canvas
    self.model = Model()
    self.nodeLocations = {}
    self.IDs = {} #not serialized, built on the fly
    self.nodesize = 20
    self.builder = ContinuousModelBuilder()
    self.varcount = 1
    self.changedCallback = None

  def modelChanged(self):
    self.model = self.builder.consume()
    if self.changedCallback is not None:
      self.changedCallback(self.model)
      
  def setCallback(self,callback):
    self.changedCallback = callback
    self.modelChanged()

  def draw(self,c):
    for k,(x,y) in self.nodeLocations.items():
      if "node-%s" % k in self.IDs:
        (nID,tID) = self.IDs["node-%s" % k]
        c.coords(nID,x-self.nodesize,y-self.nodesize,x+self.nodesize,y+self.nodesize)
        c.coords(tID,x,y)
      else:
        nID = c.create_oval(x-self.nodesize,y-self.nodesize,x+self.nodesize,y+self.nodesize,tags=["node", "nodename:%s" % k],fill="white")
        tID = c.create_text(x,y,text=k)
        self.IDs["node-%s" % k] = (nID,tID)
    for (s,e) in self.model.getLinks():
      (x0,y0) = self.nodeLocations[s.name]
      (x1,y1) = self.nodeLocations[e.name]
      vx = x1-x0
      vy = y1-y0
      dist = sqrt(vx*vx+vy*vy)
      try:
        dx = vx/dist*self.nodesize
        dy = vy/dist*self.nodesize
      except ZeroDivisionError:
        dx = dy = 0
      if "link-%s-%s" % (s.name,e.name) in self.IDs:
        lID = self.IDs["link-%s-%s" % (s.name,e.name)]
        c.coords(lID,x0+dx,y0+dy,x1-dx,y1-dy)
      else:
        lID = c.create_line(x0+dx,y0+dy,x1-dx,y1-dy,arrow=LAST,tags=["link", "linkfrom:%s" % s.name, "linkto:%s" % e.name])
        self.IDs["link-%s-%s" % (s.name,e.name)] = lID

  def addNode(self,x,y):
    name = "v%s" % self.varcount
    self.builder.addNode(name)
    self.varcount += 1
    self.nodeLocations[name] = (x,y)
    self.modelChanged()
  
  def remove(self,item):
    if "link" in self.canvas.gettags(item):
      self.removelink(item)
    elif "node" in self.canvas.gettags(item):
      self.removenode(item)
    else:
      raise AssertionError
    self.modelChanged()
  def removelink(self,item):
    nfrom = self.canvas.getAttrib(item,"linkfrom")
    nto = self.canvas.getAttrib(item,"linkto")
    self.builder.setInfluence(nfrom,nto,0)
    del self.IDs["link-%s-%s" % (nfrom,nto)]
    self.canvas.delete(item)
  def removenode(self,item):
    name = self.canvas.getAttrib(item,"nodename")
    links = list(self.canvas.find_withtag("linkto:%s" % name))
    links.extend(self.canvas.find_withtag("linkfrom:%s" % name))
    for l in links:
      self.removelink(l)
    (nID,tID) = self.IDs["node-%s" % name]
    assert(nID == item)
    self.builder.removeNode(name)
    del self.IDs["node-%s" % name]
    del self.nodeLocations[name]
    self.canvas.delete(item)
    self.canvas.delete(tID)
  def setName(self,oldname,newname):
    self.builder.setName(oldname,newname)
    v = self.nodeLocations[oldname]
    del self.nodeLocations[oldname]
    self.nodeLocations[newname] = v
    (nID,tID) = self.IDs["node-%s" % oldname]
    self.canvas.delete(nID)
    self.canvas.delete(tID)
    del self.IDs["node-%s" % oldname]
    links = list(self.canvas.find_withtag("linkto:%s" % oldname))
    links.extend(self.canvas.find_withtag("linkfrom:%s" % oldname))
    for item in links:
      nfrom = self.canvas.getAttrib(item,"linkfrom")
      nto = self.canvas.getAttrib(item,"linkto")
      del self.IDs["link-%s-%s" % (nfrom,nto)]
      self.canvas.delete(item)
    self.modelChanged()
  def setAvg(self,nodename,newavg):
    self.builder.setAvg(nodename,newavg)
    self.modelChanged()
  def setStddev(self,nodename,newstddev):
    self.builder.setStddev(nodename,newstddev)
    self.modelChanged()
  def setLevels(self,nodename,newlevels):
    self.builder.setLevels(nodename,newlevels)
    self.modelChanged()
  def setInfluence(self,s,e,influence=1.0):
    self.builder.setInfluence(s,e,influence)
    self.modelChanged()

  def __getstate__(self):
    odict = self.__dict__.copy()
    del odict['IDs']
    del odict['canvas']
    odict['changedCallback'] = None
    return odict

  def __setstate__(self, stdict):
    self.IDs = {}
    self.__dict__.update(stdict)
    #when the calling object asks us to draw, the IDs dict gets rebuild
    #calling object should set callback when interested
    #also something icky with the canvas thing

class ModelCanvas(Canvas):
  def __init__(self,parent,onModelChange=None):
    Canvas.__init__(self,parent)
    self.configure(bg="white")
    self.model = GuiModel(self)
    #self.buttonFrame should be set from outside
    self.bind("<Button-1>", self.mouseDown)
    self.bind("<ButtonRelease-1>", self.mouseUp)
    self.bind("<B1-Motion>", self.mouseDrag)
    self.bind("<Double-Button-1>", self.mouseDoubleClick)
    self.onModelChange = onModelChange
    self.model.setCallback(onModelChange)
  def findObjects(self,x,y,tags=[]):
    overlap = self.find_overlapping(x-2,y-2,x+2,y+2)
    nodes = [i for i in overlap if any(t in self.gettags(i) for t in tags)]
    if len(nodes) == 0:
      return None
    return nodes[-1]
  def getAttrib(self,item,attr):
    [a] = [n[len("%s:" % attr):] for n in self.gettags(item) if n.startswith("%s:" % attr)]
    return a
  def draw(self):
    self.model.draw(self)
  def clear(self):
    l = self.find_all()
    for i in l:
      self.delete(i)
    self.model.IDs = {}
  def load(self,filename):
    f = open(filename,"rb")
    self.model = pickle.load(f)
    f.close()
    self.model.setCallback(self.onModelChange)
    self.model.canvas = self
    self.clear()
    self.draw()
  def save(self,filename):
    f = open(filename,"wb")
    pickle.dump(self.model,f)
    f.close()

  def mouseDown(self,event):
    try:
      self.buttonFrame.currentdown.mouseDown(event, self.model, self)
      self.draw()
    except AttributeError:
      pass
  def mouseUp(self,event):
    try:
      self.buttonFrame.currentdown.mouseUp(event, self.model, self)
      self.draw()
    except AttributeError:
      pass
  def mouseDrag(self,event):
    try:
      self.buttonFrame.currentdown.mouseDrag(event, self.model, self)
      self.draw()
    except AttributeError:
      pass
  def mouseDoubleClick(self,event):
    try:
      self.buttonFrame.currentdown.mouseDoubleClick(event, self.model, self)
      self.draw()
    except AttributeError:
      pass

class ToolBarFrame(Frame):
  def __init__(self,parent):
    Frame.__init__(self,parent)
    self.currentdown = None
    
    self.buttonLoad = Button(self, command=self.buttonLoadClick)
    self.buttonLoad.configure(text="Load")
    self.buttonLoad.pack(side=LEFT)

    self.buttonSave = Button(self, command=self.buttonSaveClick)
    self.buttonSave.configure(text="Save")
    self.buttonSave.pack(side=LEFT)
    
    #TODO: separator inbetween here
    
    self.buttonSelect = SelectButton(self, command=self.buttonSelectClick)
    self.buttonSelect.pack(side=LEFT)
    self.buttonNode = NodeButton(self, command=self.buttonNodeClick)
    self.buttonNode.pack(side=LEFT)
    self.buttonInfluence = InfluenceButton(self, command=self.buttonInfluenceClick)
    self.buttonInfluence.pack(side=LEFT)
    self.buttonErase = EraseButton(self, command=self.buttonEraseClick)
    self.buttonErase.pack(side=LEFT)

    self.setCurrent(self.buttonSelect)
    #self.modelCanvas should be set from outside
    
  def setCurrent(self,button):
    if self.currentdown is not None:
      self.currentdown.config(relief=RAISED)
    self.currentdown = button
    button.config(relief=SUNKEN)
    
  def buttonLoadClick(self):
    f = tkFileDialog.askopenfilename()
    if not f=="":
      self.modelCanvas.load(f)
  def buttonSaveClick(self):
    f = tkFileDialog.asksaveasfilename()
    if not f=="":
      self.modelCanvas.save(f)
  def buttonSelectClick(self):
    self.setCurrent(self.buttonSelect)
  def buttonNodeClick(self):
    self.setCurrent(self.buttonNode)
  def buttonInfluenceClick(self):
    self.setCurrent(self.buttonInfluence)
  def buttonEraseClick(self):
    self.setCurrent(self.buttonErase)

class SelectButton(Button):
  def __init__(self, *fargs, **kw):
    Button.__init__(self, *fargs, **kw)
    self.configure(text="Select")
    self.moving = None
  def mouseDown(self, event, model, canvas):
    self.moving = canvas.findObjects(event.x,event.y,tags=["node"])
  def mouseDrag(self, event, model, canvas):
    if self.moving is None:
      return
    name = canvas.getAttrib(self.moving,"nodename")
    model.nodeLocations[name] = (event.x,event.y)
  def mouseUp(self,event, model, canvas):
    self.moving = None
  def mouseDoubleClick(self, event, model, canvas):
    editing = canvas.findObjects(event.x,event.y,tags=["node","link"])
    if editing is None:
      return
    if "link" in canvas.gettags(editing):
      nfrom = canvas.getAttrib(editing,"linkfrom")
      nto = canvas.getAttrib(editing,"linkto")
      #this about sums up how nice the design is
      oldinf = model.model.nodes[nfrom].links[model.model.nodes[nto]].influence
      d = EditInfluenceDialog(self.winfo_toplevel(),oldinf)
      if d.inf != oldinf:
        model.setInfluence(nfrom,nto,d.inf)
    elif "node" in canvas.gettags(editing):
      oldname = canvas.getAttrib(editing,"nodename")
      oldmean = model.model.nodes[oldname].avg
      oldstddev = model.model.nodes[oldname].stddev
      oldlevels = model.model.nodes[oldname].levels
      d = EditNodeDialog(self.winfo_toplevel(),oldname,oldmean,oldstddev,oldlevels)
      if d.mean != oldmean:
        model.setAvg(oldname,d.mean)
      if d.stddev != oldstddev:
        model.setStddev(oldname,d.stddev)
      if d.levels != oldlevels:
        model.setLevels(oldname,d.levels)
      if d.name != oldname:
        model.setName(oldname,d.name)
    else:
      raise AssertionError

class EditNodeDialog(tkSimpleDialog.Dialog):
  def __init__(self,master,oldname,oldmean,oldstddev,oldlevels):
    self.oldname = oldname
    self.oldmean = oldmean
    self.oldstddev = oldstddev
    self.oldlevels = " ".join(oldlevels)
    tkSimpleDialog.Dialog.__init__(self,master,"Edit Node Properties")
  def body(self, master):
    Label(master, text="Name").grid(row=0)
    Label(master, text="Mean").grid(row=1)
    Label(master, text="Standard deviation").grid(row=2)
    Label(master, text="Discretisation levels (space separated)").grid(row=3)
    self.nameE = Entry(master)
    self.nameE.insert(0,self.oldname)
    self.meanE = Entry(master)
    self.meanE.insert(0,self.oldmean)
    self.stddevE = Entry(master)
    self.stddevE.insert(0,self.oldstddev)
    self.levelsE = Entry(master)
    self.levelsE.insert(0,self.oldlevels)
    self.nameE.grid(row=0, column=1)
    self.meanE.grid(row=1, column=1)
    self.stddevE.grid(row=2, column=1)
    self.levelsE.grid(row=3, column=1)
    return self.nameE # initial focus
  def apply(self):
    self.name = self.nameE.get()
    self.mean = float(self.meanE.get())
    self.stddev = float(self.stddevE.get())
    self.levels = self.levelsE.get().split(" ")

class EditInfluenceDialog(tkSimpleDialog.Dialog):
  def __init__(self,master,oldinf):
    self.oldinf = oldinf
    tkSimpleDialog.Dialog.__init__(self,master,"Edit Influence Properties")
  def body(self, master):
    Label(master, text="Influence:").grid(row=0)
    self.infE = Entry(master)
    self.infE.insert(0,self.oldinf)
    self.infE.grid(row=0, column=1)
    return self.infE # initial focus
  def apply(self):
    self.inf = float(self.infE.get())

class NodeButton(Button):
  def __init__(self, *fargs, **kw):
    Button.__init__(self, *fargs, **kw)
    self.configure(text="Add Node")
  def mouseDown(self, event, model, canvas):
    model.addNode(event.x,event.y)
    
class InfluenceButton(Button):
  def __init__(self, *fargs, **kw):
    Button.__init__(self, *fargs, **kw)
    self.configure(text="Add Influence")
    self.tarrow = None
    self.start = None
    self.startObj = None
  def mouseDown(self, event, model, canvas):
    i = canvas.findObjects(event.x,event.y,tags=["node"])
    if i is None:
      return
    self.startObj = canvas.getAttrib(i,"nodename")
    c = canvas.coords(i)
    self.start = ((c[0] + c[2]) / 2,(c[1] + c[3]) / 2)
    self.tarrow = canvas.create_line(self.start[0],self.start[1],self.start[0],self.start[1],arrow=LAST)
  def mouseDrag(self, event, model, canvas):
    if self.tarrow is not None:
      canvas.coords(self.tarrow,self.start[0],self.start[1],event.x,event.y)
  def mouseUp(self, event, model, canvas):
    if self.tarrow is None:
      return
    canvas.delete(self.tarrow)
    self.tarrow = None
    i = canvas.findObjects(event.x,event.y,tags=["node"])
    if i is None:
      return
    model.setInfluence(self.startObj,canvas.getAttrib(i,"nodename"))
    
class EraseButton(Button):
  def __init__(self, *fargs, **kw):
    Button.__init__(self, *fargs, **kw)
    self.configure(text="Erase")
  def mouseDown(self, event, model, canvas):
    i = canvas.findObjects(event.x,event.y,tags=["link","node"])
    if i is None:
      return
    model.remove(i)
