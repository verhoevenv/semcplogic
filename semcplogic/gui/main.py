#!/usr/bin/python
# -*- coding: utf-8 -*-
from Tkinter import *
import tkMessageBox
import tkSimpleDialog
import tkFileDialog
from model import ModelCanvas,ToolBarFrame
from ..cpmodel import CPLogicGenerator,TableResultInterpreter
from ..cpcompiler import CPCompiler
from ..dataset import Dataset, fromCSV
from multilistbox import MultiListbox
from itertools import repeat

class ModelFrame(Frame):
  def __init__(self,parent,storage):
    Frame.__init__(self,parent)
    storage.addModelObserver(self)
    self.parent = parent
    self.storage = storage
    self.codegen = CPLogicGenerator()
    
    self.buttonFrame = ToolBarFrame(self)
    self.buttonFrame.pack(side=TOP)
    
    frame = Frame(self)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    xscrollbar = Scrollbar(frame, orient=HORIZONTAL)
    xscrollbar.grid(row=1, column=0, sticky=E+W)
    yscrollbar = Scrollbar(frame)
    yscrollbar.grid(row=0, column=1, sticky=N+S)
    self.cpText = Text(frame, wrap=NONE, height=4,
                xscrollcommand=xscrollbar.set,
                yscrollcommand=yscrollbar.set)
    self.cpText.grid(row=0, column=0, sticky=N+S+E+W)
    xscrollbar.config(command=self.cpText.xview)
    yscrollbar.config(command=self.cpText.yview)
    frame.pack(side=BOTTOM,expand=YES,fill=BOTH)
    
    #self.vScroll = Scrollbar(parent)
    #self.vScroll.pack(side=RIGHT, fill=Y)
    #self.cpText = Text(parent,height=4,wrap=NONE)
    #self.cpText.pack(side=BOTTOM,fill=X)
    
    self.modelCanvas = ModelCanvas(self,storage.newModel)
    self.modelCanvas.pack(side=TOP,expand=YES,fill=BOTH)
    
    self.buttonFrame.modelCanvas = self.modelCanvas
    self.modelCanvas.buttonFrame = self.buttonFrame
  def newModel(self,m):
    code = self.codegen.generate(m)
    self.cpText.configure(state=NORMAL)
    self.cpText.delete("1.0",END)
    self.cpText.insert("1.0","\n".join(code))
    self.cpText.configure(state=DISABLED)  

class DataFrame(Frame):
  def __init__(self,parent,storage):
    Frame.__init__(self,parent)
    self.storage = storage
    self.storage.addModelObserver(self)

    self.buttonFrame = Frame(self)
    self.buttonFrame.pack(side=TOP)

    self.buttonLoad = Button(self.buttonFrame, command=self.buttonLoadClick)
    self.buttonLoad.configure(text="Import dataset")
    self.buttonLoad.pack(side=LEFT)
    self.buttonSave = Button(self.buttonFrame, command=self.buttonSaveClick)
    self.buttonSave.configure(text="Export dataset")
    self.buttonSave.pack(side=LEFT)
    self.buttonClear = Button(self.buttonFrame, command=self.clearData)
    self.buttonClear.configure(text="Clear")
    self.buttonClear.pack(side=LEFT)

    self.buttonGenerate = Button(self.buttonFrame, command=self.buttonGenerateClick)
    self.buttonGenerate.configure(text="Generate...")
    self.buttonGenerate.pack(side=LEFT)
    
    self.buttonDelta = Button(self.buttonFrame, command=self.buttonDeltaClick)
    self.buttonDelta.configure(text="Take delta")
    self.buttonDelta.pack(side=LEFT)
    
    self.buttonDiscretise = Button(self.buttonFrame, command=self.buttonDiscretiseClick)
    self.buttonDiscretise.configure(text="Discretise")
    self.buttonDiscretise.pack(side=LEFT)
    
    self.tableFrame = Frame(self)
    self.tableFrame.pack(side=TOP,expand=YES,fill=BOTH)
    
    self.table = MultiListbox(self.tableFrame,(("temp1",20),("temp2",20)))
    self.table.pack(side=TOP,expand=YES,fill=BOTH)
    
  def buttonLoadClick(self):
    f = tkFileDialog.askopenfilename(filetypes=[("Comma-separated values file",".csv"),("All files",".*")])
    if not f=="":
      #TODO: this should probably do some variable name sanity checking
      d = fromCSV(f)
      self.setData(d)
  def buttonSaveClick(self):
    f = tkFileDialog.asksaveasfilename(filetypes=[("Comma-separated values file",".csv"),("All files",".*")])
    if not f=="":
      self.storage.currentDataset.toCSV(f)
  def buttonGenerateClick(self):
    self.clearData()
    d = GenerateDialog(self,dict([(n.name,n.exo) for n in self.storage.currentModel.nodes.values()]))
    if d.samples is None:
      return
    startnodes = [n for (n,e) in d.exo.items() if e]
    #TODO: catch sampling exceptions and display them
    data = self.storage.currentModel.sampleNodes(d.samples,startnodes)
    self.addData(data)
  def buttonDiscretiseClick(self):
    levels = self.storage.currentModel.getLevels()
    self.setData(self.storage.currentDataset.discretise(levels))
  def buttonDeltaClick(self):
    self.setData(self.storage.currentDataset.makeDiff())
  def clearData(self):
    self.table.delete(0,END)
    self.storage.newDataset(Dataset(self.storage.currentModel.getObservableVariables()))
  def setData(self,dataset):
    assert(len(self.table.lists) == len(dataset.getVariables()))
    self.clearData()
    self.addData(dataset)
  def addData(self,dataset):
    assert(len(self.table.lists) == len(dataset.getVariables()))
    for d in dataset.asDict():
      self.storage.currentDataset.addDictData(d)
      self.table.insert_dict(END,d)
    self.storage.newDataset(self.storage.currentDataset)
  def newModel(self,m):
    self.clearData()
    cols = self.storage.currentDataset.getVariables()
    if cols == []:
      return
    collayout = zip(cols,repeat(5))
    self.table.pack_forget()
    self.table = MultiListbox(self.tableFrame,collayout)
    self.table.pack(side=TOP,expand=YES,fill=BOTH)

class GenerateDialog(tkSimpleDialog.Dialog):
  def __init__(self,master,exonodes):
    self.exonodes = dict([(n,IntVar(value=int(e))) for n,e in exonodes.items()])
    self.samples = None
    tkSimpleDialog.Dialog.__init__(self,master,"Set options for data generations")
  def body(self, master):
    Label(master, text="Samples:").grid(row=0)
    self.sE = Entry(master)
    self.sE.insert(0,100)
    self.sE.grid(row=0, column=1)
    for i,(n,e) in enumerate(self.exonodes.items()):
      Checkbutton(master,variable=e,text=n).grid(row=i+1,column=1)
    Label(master, text="Exogenous nodes").grid(row=1,column=0,rowspan=i,sticky=N+S)
    return self.sE # initial focus
  def apply(self):
    self.samples = int(self.sE.get())
    self.exo = dict([(n,e.get()) for n,e in self.exonodes.items()])

class LearningFrame(Frame):
  def __init__(self,parent,storage):
    Frame.__init__(self,parent)
    self.storage = storage
    
    self.buttonFrame = Frame(self)
    self.buttonFrame.pack(side=TOP)
    Label(self.buttonFrame, text="Iterations:").pack(side=LEFT)
    self.entryIterations = Entry(self.buttonFrame,width=5)
    self.entryIterations.insert(0,"100")
    self.entryIterations.pack(side=LEFT)
    self.buttonLearn = Button(self.buttonFrame, command=self.buttonLearnClick)
    self.buttonLearn.configure(text="Learn")
    self.buttonLearn.pack(side=LEFT)
    
    self.tableholder = Frame(self) #this might become a canvas to get it scrollable
    self.tableholder.pack(side=TOP)
    
  def buttonLearnClick(self):
    if(not self.storage.currentDataset.isDiscretised()):
      tkMessageBox.showwarning("Warning", "Can't learn from non-discretised data!")
      return
    #TODO: might want to put some feedback on learning progress in the gui...
    cm = CPLogicGenerator()
    cpcode = cm.generate(self.storage.currentModel)
    cc = CPCompiler()
    runmodel = cc.compileCode(cpcode,self.storage.currentDataset)
    runmodel.iterations = int(self.entryIterations.get())
    result = runmodel.run()
    t = TableResultInterpreter()
    r = t.interprete(self.storage.currentModel,result.latest())
    for (nodename,restable) in r.items():
      self.addTable(nodename,restable)

  def addTable(self,name,datatable):
    f = Frame(self.tableholder,relief=RIDGE,bd=3)
    Label(f,text=name).grid(row=0,column=0,sticky=EW)
    colnames = self.storage.currentModel.nodes[name].levels
    assert(set(datatable.values()[0].keys()) == set(colnames))
    for i,n in enumerate(colnames):
      Label(f,text=n).grid(row=0,column=(i+1),sticky=EW)
    for (i,(rowname,rowdata)) in enumerate(datatable.items()):
      Label(f,text=rowname).grid(row=i+1,column=0,sticky=EW)
      for j,n in enumerate(colnames):
        #TODO: maybe round the data, maybe...
        Label(f,text=str(rowdata[n])).grid(row=(i+1),column=(j+1),sticky=EW)
    f.pack(side=TOP)
    

class StorageController:
  def __init__(self):
    self.modelObservers = []
    self.currentModel = None
    self.currentDataset = None
  def newModel(self,m):
    self.currentModel = m
    for modelobs in self.modelObservers:
      modelobs.newModel(m)
  def addModelObserver(self,obs):
    self.modelObservers.append(obs)
  def newDataset(self,d):
    self.currentDataset = d

class MainWindow:
  def __init__(self, parent):
    parent.geometry("640x480")
    self.parent = parent
    self.storage = StorageController()
    
    self.buttonFrame = Frame(parent)
    self.buttonFrame.pack(side=TOP)
    self.viewFrame = Frame(parent,bg="white")
    self.viewFrame.pack(side=TOP,expand=YES,fill=BOTH)

    self.buttonModel = Button(self.buttonFrame, command=self.buttonModelClick)
    self.buttonModel.configure(text="Model")
    self.buttonModel.pack(side=LEFT)
    self.frameModel = ModelFrame(parent,self.storage)

    self.buttonData = Button(self.buttonFrame, command=self.buttonDataClick)
    self.buttonData.configure(text="Data")
    self.buttonData.pack(side=LEFT)
    self.frameData = DataFrame(parent,self.storage)
    
    self.buttonLearn = Button(self.buttonFrame, command=self.buttonLearnClick)
    self.buttonLearn.configure(text="Learn")
    self.buttonLearn.pack(side=LEFT)
    self.frameLearn = LearningFrame(parent,self.storage)
    
    self.currentdown = None
    self.buttonModelClick()
    
  def setFrame(self,newframe):
    self.viewFrame.pack_forget()
    self.viewFrame = newframe
    self.viewFrame.pack(side=TOP,expand=YES,fill=BOTH)
  
  def setCurrent(self,button):
    if self.currentdown is not None:
      self.currentdown.config(relief=RAISED)
    self.currentdown = button
    button.config(relief=SUNKEN)

  def buttonModelClick(self):
    self.setCurrent(self.buttonModel)
    self.setFrame(self.frameModel)

  def buttonDataClick(self):
    self.setCurrent(self.buttonData)
    self.setFrame(self.frameData)
  
  def buttonLearnClick(self):
    self.setCurrent(self.buttonLearn)
    self.setFrame(self.frameLearn)
