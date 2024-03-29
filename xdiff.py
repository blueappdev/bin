#!/usr/bin/env python
#
# xdiff.py (python3 version)
#

import os
import sys
import string
import getopt
import time
import tkinter
from tkinter import simpledialog
from tkinter import messagebox

def matchLongOption(arg,opt):
    x=string.find(opt, "/")
    return len(arg) >= x and (opt[:x] + opt[x + 1:])[:len(arg)] == arg

class MessageDialog(simpledialog.Dialog):
    def  __init__(self, parent, title = "titleString", text="messageString"):
        self.titleString = title
        self.messageString = text
        simpledialog.Dialog.__init__(self,parent)

    def buttonbox(self):
        box = tkinter.Frame(self)
        self.button = tkinter.Button(box, 
                text = "OK", width = 10, 
                command = self.ok, default = tkinter.ACTIVE)
        self.button.pack(side = tkinter.LEFT, padx = 5, pady = 5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)
        box.pack()

    def body(self,master):
        self.title(self.titleString)
        #self.messageLabel = tkinter.Label(master, width = 16, text = self.messageString)
        self.messageLabel = tkinter.Label(master, text = self.messageString)
        #self.messageLabel.grid(row = 0, column = 1, stick = tkinter.W)
        self.messageLabel.grid()
        return None # self.button # for focus_set

class FindDialog(simpledialog.Dialog):
    def __init__(self,parent,defaultFindString = ""):
        self.defaultFindString = defaultFindString
        simpledialog.Dialog.__init__(self,parent)
        
    def body(self,master):
        self.title("Find")
        self.findString = None
        self.findStringVar = tkinter.StringVar()
        if self.defaultFindString is None: 
            self.findStringVar.set("")
        else:
            self.findStringVar.set(self.defaultFindString)
        tkinter.Label(master,text="Find:").grid(
            row = 0,column = 0,
            stick = tkinter.W)
        self.entry = tkinter.Entry(master,textvariable = self.findStringVar,
            background = "white")
        self.entry.grid(row = 0,column = 1,
            columnspan = 4, stick = tkinter.EW)
        self.entry.selection_range(0,tkinter.END)
        self.entry.icursor(tkinter.END)
        self.findInWhatWindow = tkinter.StringVar()
        self.findInWhatWindow.set("left")
        self.findDirection = tkinter.IntVar()
        self.findDirection.set(1)
        self.findIgnoreCase = tkinter.IntVar()
        self.findIgnoreCase.set(1)
        rb = tkinter.Radiobutton(master,
                text = "Forward",
                variable = self.findDirection,
                value = 1)
        rb.grid(row = 1, column = 1, stick = tkinter.W)
        rb = tkinter.Radiobutton(master,
                text = "Backward",
                variable = self.findDirection,
                value = -1)
        rb.grid(row = 2, column = 1, stick = tkinter.W)
        rb = tkinter.Checkbutton(master,
                text = "Ignore Case",
                variable = self.findIgnoreCase)
        rb.grid(row = 1,column = 2, stick = tkinter.W)
        rb = tkinter.Radiobutton(master,
                text = "Left Window",
                variable = self.findInWhatWindow,
                value = "left")
        rb.grid(row = 1, column = 3, stick = tkinter.W)
        rb=tkinter.Radiobutton(master,
                text="Right Window",
                variable=self.findInWhatWindow,
                value="right")
        rb.grid(row=2,column=3,stick=tkinter.W)
        return self.entry #for focus_set

    def apply(self):
        self.findString=self.entry.get()

def splitblank(s):
    # splits a string into fields,
    # the spearators are also fields
    result = []
    ftype = 2
    for c in s:
        ctype = c in [ " ", "\t", "\n", "\r" ] 
        if ctype != ftype:
           result.append("")
           ftype = ctype
        result[-1] = result[-1] + c
    return result

def prepareLineForDiff(line,ignoreBlankFlagString):
    lineData = []
    for i in range(len(line)):
        ch = line[i]
        if ignoreBlankFlagString == "-w":
            if ch not in [ " ", "\t", "\r", "\n" ]:
                lineData.append((ch,i))
        else:
            lineData.append((ch,i))
    #print lineData
    return lineData

def onelinediff(leftLine,rightLine):
    onelinediff1(leftLine,rightLine)
    leftLineData = prepareLineForDiff(leftLine,ignoreBlankFlagString)
    rightLineData = prepareLineForDiff(rightLine,ignoreBlankFlagString)
    x=0
    y1=len(leftLineData)-1
    y2=len(rightLineData)-1
    xmax=min(y1,y2)
    while x<=xmax:
        if leftLineData[x][0] != rightLineData[x][0]:
            break
        x=x+1
    # x points now to the first different character of the line
   
    y=0
    while y1-y>x and y2-y>x:
        if leftLineData[y1-y][0] != rightLineData[y2-y][0]:
            break
        y=y+1
    # y points to first different character from the end
    #print x,y,leftLineData[y][1],y1

    xdleft = leftLineData[x][1]
    xdright = rightLineData[x][1]
    ydleft = len(leftLine)-leftLineData[y1-y][1]-1
    ydright = len(rightLine)-rightLineData[y2-y][1]-1

    result = (xdleft,ydleft,xdright,ydright)
    #print "result=",result
    return result

def onelinediff1(leftLine,rightLine):
    x=0
    y1=len(leftLine)-1
    y2=len(rightLine)-1
    xmax=min(y1,y2)
    while x<=xmax:
        if leftLine[x] != rightLine[x]:
            break
        x=x+1
    # x points now to the first different character of the line

    y=0
    while y1-y>x and y2-y>x:
        if leftLine[y1-y] != rightLine[y2-y]:
            break
        y=y+1
    # y points to first different character from the end
    #print "onelinediffold",(x,y,x,y)
    return (x,y,x,y)


class DiffTool(tkinter.Frame):
    def __init__(self,master):
        self.createPopupMenus()
        self.horizontalScrollbarUpdateInfo=10
        self.verticalScrollbarUpdateInfo=10
        self.findString=None
        self.navigationList=[]
        self.navigationIndex=None
        tkinter.Frame.__init__(self,master=master)
        self.master.protocol("WM_DELETE_WINDOW",self.onFileExit)

        # Send explicitly the unpost context menu, 
        # whenever the mouse button is pressed
        # (The context menu does not disappear on Unix, 
        # when clicked outside the context menu.) 
        self.master.bind("<Button-1>",self.unpostContextMenus)

        self.pack()
        self.createMenubar()
        self.createToolbar()
        self.createStatusLine()

        self.mainFrame=tkinter.Frame(self.master,width=1200,height=720)
        self.master.bind("<Control-f>", self.onViewFind)
        self.master.bind("<F3>", self.onViewFindAgain)

        #
        # Left Frame
        #
        self.leftFrame = tkinter.Frame(self.mainFrame)
        self.leftLabel = tkinter.Entry(self.leftFrame, bd=1, relief=tkinter.SUNKEN)
        self.leftLabel.pack(side=tkinter.TOP,fill=tkinter.X)
        self.leftVerticalScrollbar=tkinter.Scrollbar(self.leftFrame, 
                orient = tkinter.VERTICAL)
        self.leftHorizontalScrollbar=tkinter.Scrollbar(self.leftFrame, 
                orient = tkinter.HORIZONTAL)
        self.leftText = tkinter.Text(self.leftFrame,
                bg="white",
                xscrollcommand=self.leftxset,
                yscrollcommand=self.leftyset)
        if os.name == "nt":
            self.leftText.config(font=("Courier",8))
        self.leftText.config(wrap=tkinter.NONE)
        self.leftVerticalScrollbar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        self.leftHorizontalScrollbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
        self.leftText.pack(fill=tkinter.BOTH,expand=1)
        #self.leftFrame.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)
        #self.leftFrame.grid(row=0,column=0,stick=tkinter.NSEW,expand=1)
        self.leftFrame.place(relwidth=0.5,width=-7,relheight=1)

        self.leftText.bind("<Key>", self.filterKey)
        self.leftText.bind("<Button-3>", self.popupLeftMenu)
        self.leftLabel.bind("<Key>", self.filterKey)
        self.leftLabel.bind("<Button-3>", self.popupLeftMenu)

        #
        # Right Frame
        #
        self.rightFrame = tkinter.Frame(self.mainFrame)
        self.rightLabel = tkinter.Entry(self.rightFrame, bd = 1, relief = tkinter.SUNKEN)
        self.rightLabel.pack(side = tkinter.TOP, fill = tkinter.X)
        self.rightVerticalScrollbar = tkinter.Scrollbar(self.rightFrame, 
                orient = tkinter.VERTICAL)
        self.rightHorizontalScrollbar = tkinter.Scrollbar(self.rightFrame, 
                orient = tkinter.HORIZONTAL)
        self.rightText = tkinter.Text(self.rightFrame,
                bg="white",
                xscrollcommand = self.rightxset,
                yscrollcommand = self.rightyset)
        if os.name == "nt":
            self.rightText.config(font=("Courier",8))
        self.rightText.config(wrap=tkinter.NONE)
        self.rightVerticalScrollbar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        self.rightHorizontalScrollbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
        self.rightText.pack(fill=tkinter.BOTH,expand=1)
        #self.rightFrame.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)
        #self.rightFrame.grid(row=0,column=1,stick=tkinter.NSEW,expand=1)
        self.rightFrame.place(relx=0.5,x=-7,width=-7,relwidth=0.5,relheight=1)

        self.rightText.bind("<Key>", self.filterKey)
        self.rightText.bind("<Button-3>", self.popupRightMenu)
        self.rightLabel.bind("<Key>", self.filterKey)
        self.rightLabel.bind("<Button-3>", self.popupRightMenu)

        # connect scrollbars with widgets
        self.leftVerticalScrollbar.config(command=self.yview)
        self.leftHorizontalScrollbar.config(command=self.xview)
        self.rightVerticalScrollbar.config(command=self.yview)
        self.rightHorizontalScrollbar.config(command=self.xview)

        self.canvas=tkinter.Canvas(self.mainFrame,background="white")
        self.canvas.place(relx=1,x=-14,width=14,relheight=1,height=-52,y=35)
        self.canvas.place(relx=1,x=-14,width=14,relheight=1,height=-52,y=35)
        self.canvas.bind("<Configure>", self.canvasChanged)
        
        #
        self.mainFrame.pack(fill=tkinter.BOTH,expand=1)

    def canvasChanged(self,event):
        # canvas size changed, re-paint all rectangles
        self.canvas.delete(tkinter.ALL)
        a = 0  # cumulatation of lines
        b = 0 
        leftdelta=0
        rightdelta=0
        for t,lefta,leftb,righta,rightb in self.diffRecords:
            assert(self.leftText.index(tkinter.END) == self.rightText.index(tkinter.END))
            x, y = map(int, self.leftText.index(tkinter.END).split("."))
            a = max(lefta + leftdelta, righta + rightdelta)
            b = a + max(leftb - lefta, rightb - righta) + 1
            #print t,lefta,"(",lefta+leftdelta,")",leftb,righta,"(",righta+rightdelta,")",rightb,a,b
            if t=="a":
                self.canvas.create_rectangle(0,(a - 1) * event.height/x,14,(b - 1)*event.height/x,fill="red",outline="red")
                leftdelta=leftdelta + rightb - righta + 1
            if t=="d":
                self.canvas.create_rectangle(0,(a-1)*event.height/x,14,(b - 1) * event.height/x,fill="green",outline="green")
                rightdelta=rightdelta + leftb - lefta + 1
            if t=="c":
                self.canvas.create_rectangle(0,(a-1)*event.height/x,14,(b - 1) * event.height/x,fill="blue",outline="blue")
                d=(leftb - lefta) - (rightb - righta)
                if d<0:
                    leftdelta=leftdelta + abs(d) + 1
                if d>0:
                    rightdelta=rightdelta + abs(d) + 1
                    

    def leftxset(self,a,b):
        if self.horizontalScrollbarUpdateInfo==40:
            self.horizontalScrollbarUpdateInfo=0
            self.leftHorizontalScrollbar.set(a,b)
            self.rightHorizontalScrollbar.set(a,b)
        elif self.horizontalScrollbarUpdateInfo==0:
            pass
        elif self.horizontalScrollbarUpdateInfo==20:
            self.leftHorizontalScrollbar.set(a,b)
            self.rightHorizontalScrollbar.set(a,b)
        elif self.horizontalScrollbarUpdateInfo==10:
            self.horizontalScrollbarUpdateInfo=0
            self.leftHorizontalScrollbar.set(a,b)
            self.rightHorizontalScrollbar.set(a,b)
            self.leftText.xview("moveto",a)
            self.rightText.xview("moveto",a)
            self.mainFrame.update_idletasks()
            self.horizontalScrollbarUpdateInfo=10
        else:
            assert(0)

    def rightxset(self,a,b):
        self.leftxset(a,b)

    def leftyset(self,a,b):
        if self.verticalScrollbarUpdateInfo==40:
            self.verticalScrollbarUpdateInfo=0
            self.leftVerticalScrollbar.set(a,b)
            self.rightVerticalScrollbar.set(a,b)
        elif self.verticalScrollbarUpdateInfo==0:
            pass
        elif self.verticalScrollbarUpdateInfo==20:
            self.leftVerticalScrollbar.set(a,b)
            self.rightVerticalScrollbar.set(a,b)
        elif self.verticalScrollbarUpdateInfo==10:
            self.verticalScrollbarUpdateInfo=0
            self.leftVerticalScrollbar.set(a,b)
            self.rightVerticalScrollbar.set(a,b)
            self.leftText.yview("moveto",a)
            self.rightText.yview("moveto",a)
            self.mainFrame.update_idletasks()
            self.verticalScrollbarUpdateInfo=10
        else:
            assert(0)

    def rightyset(self,a,b):
        self.leftyset(a,b)

    def xview(self,*a):
        self.horizontalScrollbarUpdateInfo=20
        if len(a)==2:
            self.leftText.xview(a[0],a[1])
            self.rightText.xview(a[0],a[1])
        elif len(a)==3:
            self.leftText.xview(a[0],a[1],a[2])
            self.rightText.xview(a[0],a[1],a[2])
        else:
            assert(0)
        self.mainFrame.update_idletasks()
        self.horizontalScrollbarUpdateInfo=10

    def yview(self,*a):
        self.verticalScrollbarUpdateInfo=20
        if len(a)==2:
            self.leftText.yview(a[0],a[1])
            self.rightText.yview(a[0],a[1])
        elif len(a)==3:
            self.leftText.yview(a[0],a[1],a[2])
            self.rightText.yview(a[0],a[1],a[2])
        else:
            assert(0)
        self.mainFrame.update_idletasks()
        self.verticalScrollbarUpdateInfo=10

    def createStatusLine(self):
        self.statusFrame=tkinter.Frame(self.master)
        self.statusLabel = tkinter.Label(
                self.statusFrame,
                text="status",
                bd=1,
                relief=tkinter.SUNKEN,
                anchor=tkinter.W)
        self.statusLabel.pack(side=tkinter.LEFT,fill=tkinter.X,expand=1)
        self.linesLabel = tkinter.Label(
                self.statusFrame,
                text="lines",
                bd=1,
                relief=tkinter.SUNKEN,
                anchor=tkinter.W)
        self.linesLabel.pack(side=tkinter.RIGHT,fill=tkinter.X,expand=1)
        self.statusFrame.pack(side=tkinter.BOTTOM,fill=tkinter.X)

    def createMenubar(self):
        mb = tkinter.Menu()
        self.createFileMenu(mb)
        self.createViewMenu(mb)
        self.createTestMenu(mb)
        self.master.config(menu=mb)

    def createFileMenu(self,parentMenu):
        m = tkinter.Menu(parentMenu, tearoff=0)
        parentMenu.add_cascade(label="File", menu=m)
        m.add_command(label="Exit", command=self.onFileExit)

    def createViewMenu(self,parentMenu):
        m = tkinter.Menu(parentMenu, tearoff=0)
        parentMenu.add_cascade(label="View", menu=m)
        m.add_command(
                label="Find...", 
                command=self.onViewFind,
                accelerator="Ctrl+F")
        m.add_command(
                label="Find Again", 
                command=self.onViewFindAgain,
                accelerator="F3")

    def createTestMenu(self,parentMenu):
        m = tkinter.Menu(parentMenu, tearoff=0)
        parentMenu.add_cascade(label="Test", menu=m)
        m.add_command(label="Dump", command=self.onTestDump)
        m.add_command(label="Test", command=self.onTestTest)

    def setStatus(self,s):
        self.statusLabel["text"]=s

    def createToolbar(self):
        self.buttonFrame=tkinter.Frame(self.master)

        l=tkinter.Label(self.buttonFrame,text="Changed",background="lightblue");
        l.pack(side=tkinter.RIGHT,padx=2,pady=2)
        l=tkinter.Label(self.buttonFrame,text="Deleted",background="lightgreen");
        l.pack(side=tkinter.RIGHT,padx=2,pady=2)
        l=tkinter.Label(self.buttonFrame,text="Added",background="pink");
        l.pack(side=tkinter.RIGHT,padx=2,pady=2)

        self.buttonFirstDiff=tkinter.Button(self.buttonFrame,text="<<",width=2,
                state=tkinter.DISABLED,
                command=self.navigateToFirstDiff)
        self.buttonFirstDiff.pack(side=tkinter.LEFT,padx=2,pady=2)
        self.buttonPreviousDiff=tkinter.Button(self.buttonFrame,text="<",
                state=tkinter.DISABLED,
                command=self.navigateToPreviousDiff)
        self.buttonPreviousDiff.pack(side=tkinter.LEFT,padx=2,pady=2)
        self.buttonNextDiff=tkinter.Button(self.buttonFrame,text=">",
                state=tkinter.DISABLED,
                command=self.navigateToNextDiff)
        self.buttonNextDiff.pack(side=tkinter.LEFT,padx=2,pady=2)
        self.buttonLastDiff=tkinter.Button(self.buttonFrame,text=">>",
                state=tkinter.DISABLED,
                command=self.navigateToLastDiff)
        self.buttonLastDiff.pack(side=tkinter.LEFT,padx=2,pady=2)

        self.buttonNextRedGreenDiff=tkinter.Button(self.buttonFrame,text="Next Red/Green",
                state=tkinter.NORMAL,
                command=self.navigateToNextRedGreenDiff)
        self.buttonNextRedGreenDiff.pack(side=tkinter.RIGHT,padx=2,pady=2)

        self.buttonFrame.pack(side=tkinter.TOP,fill=tkinter.X)
  
    def navigateToFirstDiff(self):
        self.buttonFirstDiff.focus()
        if (self.navigationIndex is None) and (len(self.navigationList) != 0):
            self.navigationIndex=0
        if self.navigationIndex>0:
            self.navigationIndex=0
        self.navigateToIndex(-1)

    def navigateToPreviousDiff(self):
        self.buttonPreviousDiff.focus()
        if self.navigationIndex>0:
            self.navigationIndex=self.navigationIndex-1
        self.navigateToIndex(-1)

    def navigateToNextDiff(self):
        self.buttonNextDiff.focus()
        if (self.navigationIndex is None):
            self.navigationIndex=0
        else:
            if self.navigationIndex<len(self.navigationList)-1:
                self.navigationIndex=self.navigationIndex+1
        self.navigateToIndex(1)

    # navigate to the next green or red difference (insertionsi or removals)
    # but skip all blue differences (changes)
    def navigateToNextRedGreenDiff(self):
        self.buttonNextRedGreenDiff.focus()
        backupNavigationIndex=self.navigationIndex
        if (self.navigationIndex is None):
            self.navigationIndex=0
        else:
            self.navigationIndex=self.navigationIndex+1
        # find the next red/green navigation index
        while self.navigationIndex<len(self.navigationList):
            a,b,colorTag=self.navigationList[self.navigationIndex]
            #print a,b,colorTag,self.navigationIndex
            if colorTag == "red" or colorTag == "green":
                self.navigateToIndex(1)
                return
            self.navigationIndex=self.navigationIndex+1
        self.navigationIndex = backupNavigationIndex 
           
    def navigateToLastDiff(self):
        self.buttonLastDiff.focus()
        if (self.navigationIndex is None) or (self.navigationIndex<len(self.navigationList)-1):
            self.navigationIndex=len(self.navigationList)-1
        self.navigateToIndex(1)

    def navigateToIndex(self,direction=1):
        if self.navigationIndex is None:
            self.buttonFirstDiff.config(state=tkinter.DISABLED)
            self.buttonPreviousDiff.config(state=tkinter.DISABLED)
            if len(self.navigationList)==0:
                self.buttonLastDiff.config(state=tkinter.DISABLED)
                self.buttonNextDiff.config(state=tkinter.DISABLED)
            else:
                self.buttonLastDiff.config(state=tkinter.NORMAL)
                self.buttonNextDiff.config(state=tkinter.NORMAL)
        else:
            a,b,colorTag=self.navigationList[self.navigationIndex]
            n = self.leftText.tag_names("%d.0" % a)
            n = [x for x in n if x != "sel" and x != "highlight"]
            if len(n) != 1:
                print(n)
                assert(len(n)==1)
            t="dark"+n[0]
            if t == "darkbluediffchar":
                t="darkblue"

            self.leftText.tag_config("highlight",background=t,foreground="white")
            self.rightText.tag_config("highlight",background=t,foreground="white")

            self.leftText.tag_remove("highlight",1.0,tkinter.END)
            self.rightText.tag_remove("highlight",1.0,tkinter.END)
        
            self.leftText.tag_add("highlight","%d.0" % a,"%d.0" % b)
            self.rightText.tag_add("highlight","%d.0" % a,"%d.0" % b)

            x = 0  
            y = 0
            if t == "darkblue":
                leftString = leftData[a-1][0]
                rightString = rightData[a-1][0]
                xdleft,ydleft,xdright,ydright = onelinediff(leftString,rightString)
                x = xdleft
                y = ydleft

            if self.leftText.bbox("%d.%d" % (b,x)) is None or self.leftText.bbox("%d.%d" % (a,x)) is None:
                self.verticalScrollbarUpdateInfo=40
                self.horizontalScrollbarUpdateInfo=40
                if direction == 1:
                    self.leftText.see("%d.%d" % (min(b+10000,self.totalLines),x))
                    self.rightText.see("%d.%d" % (min(b+10000,self.totalLines),x))
                    self.leftText.see("%d.%d" % (a,x))
                    self.rightText.see("%d.%d" % (a,x))
                elif direction == -1:
                    self.leftText.see("%d.%d" % (max(a-10000,0),x))
                    self.rightText.see("%d.%d" % (max(a-10000,0),x))
                    self.leftText.see("%d.%d" % (b,x))
                    self.rightText.see("%d.%d" % (b,x))
                self.mainFrame.update_idletasks()
                self.verticalScrollbarUpdateInfo=10
                self.horizontalScrollbarUpdateInfo=10

            if self.navigationIndex==0:
                self.buttonFirstDiff.config(state=tkinter.DISABLED)
                self.buttonPreviousDiff.config(state=tkinter.DISABLED)
            else:
                self.buttonFirstDiff.config(state=tkinter.NORMAL)
                self.buttonPreviousDiff.config(state=tkinter.NORMAL)

            if self.navigationIndex>=len(self.navigationList)-1:
                self.buttonLastDiff.config(state=tkinter.DISABLED)
                self.buttonNextDiff.config(state=tkinter.DISABLED)
            else:
                self.buttonLastDiff.config(state=tkinter.NORMAL)
                self.buttonNextDiff.config(state=tkinter.NORMAL)

    def onFileExit(self):
        self.quit()

    def findAction(self):
        if self.findIgnoreCase:
            actualFindString = self.findString.upper()
        else:
            actualFindString = self.findString

        # take current start position for find/search from
        #     - current selection
        #     - current insertion cursor
        #     - begin (or end for backward search) of file

        selectionRange = self.findTextWidget.tag_ranges(tkinter.SEL)
        if len(selectionRange) == 0:
            insertIndex = self.findTextWidget.index(tkinter.INSERT)
            if insertIndex != self.findTextWidget.index("%s-1c" % tkinter.END):
                # insert-index available 
                newFindIndex = insertIndex
            else:
                # insert-index not available 
                if self.findDirection == 1: # forward search
                    newFindIndex = "1.0"
                else:  # backward search
                    newFindIndex = self.findTextWidget.index(tkinter.END) 
        else:
            if self.findDirection == 1: 
                # forward search
                newFindIndex = selectionRange[0]
                newFindIndex = self.findTextWidget.index("%s+1c" % selectionRange[0])
            else:  
                # backward search
                newFindIndex = selectionRange[1]
                newFindIndex = self.findTextWidget.index("%s-1c" % selectionRange[1])

        if self.findDirection == 1: 
            # forward search
            findData = self.findTextWidget.get(newFindIndex,tkinter.END)
        else:  
            # backward search
            findData = self.findTextWidget.get("1.0",newFindIndex)

        if self.findIgnoreCase:
            findData = findData.upper()

        if self.findDirection == 1:
            distance = findData.find(actualFindString)
        else:
            distance = findData.rfind(actualFindString)
          
        if distance >= 0:
            if self.findDirection == 1:
                newFindIndex = self.findTextWidget.index("%s+%dc" % (newFindIndex, distance))
            else:
                newFindIndex = self.findTextWidget.index("%s+%dc" % ("1.0", distance))
            beginSelectionIndex = newFindIndex
            endSelectionIndex = self.findTextWidget.index("%s+%sc" % (newFindIndex, len(actualFindString))) 
            self.leftText.tag_remove(tkinter.SEL, 1.0, tkinter.END)
            self.rightText.tag_remove(tkinter.SEL, 1.0, tkinter.END)
       
            # The widget must have focus (on Windows platform),
            # otherwise tag SEL is ignored.
            self.findTextWidget.focus() 
            self.findTextWidget.tag_add(tkinter.SEL,beginSelectionIndex,endSelectionIndex)
            self.findTextWidget.mark_set(tkinter.INSERT,endSelectionIndex)

            if (self.findTextWidget.bbox(beginSelectionIndex) is None or 
                    self.findTextWidget.bbox(endSelectionIndex) is None):
                if self.findDirection == 1:
                    line,col=string.split(beginSelectionIndex,".")
                    self.findTextWidget.see("%d.%d" % 
                            (min(int(line)+10000,self.totalLines),
                             int(col)))
                    self.findTextWidget.see(endSelectionIndex)
                    self.findTextWidget.see(beginSelectionIndex)
                elif self.findDirection == -1:
                    line,col=string.split(endSelectionIndex,".")
                    self.findTextWidget.see("%d.%d" % 
                            (min(int(line)-10000,self.totalLines),
                             int(col)))
                    self.findTextWidget.see(beginSelectionIndex)
                    self.findTextWidget.see(endSelectionIndex)
        else:
            MessageDialog(self.master,
                    "Not found",
                    self.findString+" not found in "+self.findInWhatWindow+" window.")

        
    def onViewFind(self,event=None):
        dlg=FindDialog(self.master,defaultFindString=self.findString)
        if dlg.findString is not None:
            self.findString = dlg.findString
        # Do not modify self.findString if "Cancel" was pressed in FindDialog.
        if dlg.findString is not None and self.findString != "":
            self.findInWhatWindow=dlg.findInWhatWindow.get()
            self.findIgnoreCase=dlg.findIgnoreCase.get()
            if self.findInWhatWindow=="right":
                self.findData=rightData
                self.findTextWidget = self.rightText
            else:
                self.findData=leftData
                self.findTextWidget = self.leftText
            self.findDirection=dlg.findDirection.get()
            if self.findDirection == 1:   # find forward
                self.currentFindLine=0
            else:
                self.currentFindLine=self.totalLines-1
            self.findAction()

    def onViewFindAgain(self,dummyEvent=None):
        if self.findString is None or self.findString == "":
            self.onViewFind()
        else:
            self.currentFindLine=self.currentFindLine+self.findDirection
            self.findAction()

    def createPopupMenus(self):
        self.standardEditor = os.environ.get("EDITOR","").strip()
        self.leftPopupMenu = tkinter.Menu(tearoff=0)
        self.rightPopupMenu = tkinter.Menu(tearoff=0)
        if self.standardEditor != "":
            self.leftPopupMenu.add_command(
                    label="Edit (" + self.standardEditor+") left file", 
                    command=self.editLeftFile)
            self.rightPopupMenu.add_command(
                    label="Edit (" + self.standardEditor + ") right file", 
                    command=self.editRightFile)
        if os.name == "nt":
            self.leftPopupMenu.add_command(label="Notepad",command=self.notepadLeftFile)
            self.rightPopupMenu.add_command(label="Notepad",command=self.notepadRightFile)
            self.leftPopupMenu.add_command(label="Wordpad",command=self.wordpadLeftFile)
            self.rightPopupMenu.add_command(label="Wordpad",command=self.wordpadRightFile)
        else:
            self.leftPopupMenu.add_command(label="nedit", command=self.neditLeftFile)
            self.leftPopupMenu.add_command(label="xemacs", command=self.xemacsLeftFile)
            self.leftPopupMenu.add_command(label="vi", command=self.viLeftFile)
            self.rightPopupMenu.add_command(label="nedit", command=self.neditRightFile)
            self.rightPopupMenu.add_command(label="xemacs", command=self.xemacsRightFile)
            self.rightPopupMenu.add_command(label="vi", command=self.viRightFile)

    def popupLeftMenu(self,ev):
        self.unpostContextMenus()
        self.leftPopupMenu.post(ev.x_root,ev.y_root)

    def popupRightMenu(self,ev):
        self.unpostContextMenus()
        self.rightPopupMenu.post(ev.x_root,ev.y_root)

    def unpostContextMenus(self,ev=None):
        self.leftPopupMenu.unpost()
        self.rightPopupMenu.unpost()

    def startEditor(self,editor,file):
        cmd = editor + " " + file + " &"
        rc = os.system(cmd)
        if rc is not None and rc != 0:
            print("\""+cmd+"\" returned "+str(rc))

    def neditLeftFile(self):
        self.startEditor("nedit",self.fileName1)
    
    def xemacsLeftFile(self):
        self.startEditor("xemacs",self.fileName1)

    def viLeftFile(self):
        self.startEditor("xterm -e vi",self.fileName1)

    def editLeftFile(self):
        self.startEditor("xterm -e "+self.standardEditor,self.fileName1)

    def neditRightFile(self):
        self.startEditor("nedit",self.fileName2)
    
    def xemacsRightFile(self):
        self.startEditor("xemacs",self.fileName2)

    def viRightFile(self):
        self.startEditor("xterm -e vi",self.fileName2)

    def editRightFile(self):
        self.startEditor("xterm -e "+self.standardEditor,self.fileName2)

    def notepadLeftFile(self):
        self.startEditor("notepad",self.fileName1)

    def notepadRightFile(self):
        self.startEditor("notepad",self.fileName2)

    def wordpadLeftFile(self):
        self.startEditor("write",self.fileName1)

    def wordpadRightFile(self):
        self.startEditor("write",self.fileName2)

    def onTestDump(self):
        MessageDialog(self.master, "Not implemented", "onTestDump not implemented")

    def onTestTest(self):
        MessageDialog(self.master, "Not implemented", "onTestTest not implemented")
        #self.leftText.focus()
        #self.leftText.tag_add(tkinter.SEL,"1.0","1.5")

    def filterKey(self,ev):
        # Filter all keys which might modify the text.

        #print "sym=<"+ev.keysym+">, code=<"+str(ev.keycode)+">, chr=<"+ev.char+">, state= <"+str(ev.state)+">"

        controlKeyDown = ev.state & 4
        
        if ev.keysym in [ "Left", "Right", "Up", "Down",
                          "Prior", "Next", "Home", "End",
                          "Escape", "F3" ]:
            return

        if controlKeyDown and ev.keysym in [ "f", "c", "x" ]:
            return
        
        # The event ev is considered as representing a key, 
        # which would modify the text, which is not what is wanted.
        return "break"

def usage(msg=None):
    if msg is not None:
        sys.stderr.write("xdiff: ERROR: ")
        sys.stderr.write(msg)
        sys.stderr.write("\n\n")
    sys.stderr.write("xdiff.py: diff two files\n")
    sys.stderr.write("Usage: xdiff.py [ options ] file1 file2\n")
    sys.stderr.write("Options:\n")
    sys.stderr.write("    -w                  Unix diff -w (ignores all blanks)\n")
    sys.stderr.write("    -b                  Unix diff -b (ignores trailing blanks)\n")
    sys.exit(2)

if __name__ == "__main__":
   fileName1 = None
   fileName2 = None

   # default values
   ignoreBlankFlagString = ""

   for arg in sys.argv[1:]:
       if arg[:1] == "-":
           if arg == "-w":
               ignoreBlankFlagString = "-w"
           elif arg == "-b":
               ignoreBlankFlagString = "-b"
           else:
               usage("Unknown command line option\""+arg+"\" for Unix-diff.")
       else:
           if fileName1 is None:
               fileName1 = arg
           else:
               if fileName2 is None:
                   fileName2 = arg
               else:
                   usage("Too many parameters.")

   if fileName1 is None or fileName2 is None:
       usage("Two file names expected.")

   try: 
       tk = tkinter.Tk()
   except tkinter.TclError as ex:
       print(ex)
       sys.exit(2)

   tk.title("xdiff")

   tool = DiffTool(tk)
   tool.diffRecords=[]

   try:
       tool.leftLabel.insert(tkinter.END,fileName1)
       tool.fileName1 = fileName1

       leftData = []
       leftStream = open(fileName1)
       line=leftStream.readline()
       while line != "":
           leftData.append([line, None])
           line=leftStream.readline()
       leftStream.close()

       tool.rightLabel.insert(tkinter.END, fileName2)
       tool.fileName2 = fileName2

       rightData=[]
       rightStream=open(fileName2)
       line=rightStream.readline()
       while line != "":
           rightData.append([line, None])
           line=rightStream.readline()
       rightStream.close()

       diffCommand = "diff"
       if ignoreBlankFlagString != "":
           diffCommand = diffCommand + " " + ignoreBlankFlagString
       diffCommand = diffCommand + " " + fileName1 + " " + fileName2

       #print(diffCommand)
       with os.popen(diffCommand) as stream:
           for diffLine in stream:
               diffLine = diffLine.rstrip()
               if (len(diffLine) >= 1 and
                   diffLine[0] != ">" and
                   diffLine[0] != "<" and
                   diffLine != "---"):
                   #print(diffLine)
                   for x in ["a", "c", "d"]:
                       fields = diffLine.split(x)
                       assert(len(fields) == 1 or len(fields) == 2)
                       if len(fields) == 2:
                           leftfields = fields[0].split(",")
                           assert(len(leftfields) <= 2)
                           a1 = int(leftfields[0])
                           if len(leftfields) == 1:
                               a2 = a1
                           else:
                               a2 = int(leftfields[1])
                           rightfields = fields[1].split(",")
                           assert(len(rightfields) <= 2)
                           b1 = int(rightfields[0])
                           if len(rightfields) == 1:
                               b2 = b1
                           else:
                               b2 = int(rightfields[1])
                           tool.diffRecords.append((x,a1,a2,b1,b2))

       # print "diffRecords:", tool.diffRecords

       if len(tool.diffRecords) == 0: 
           msg = "No differences found."
           print(msg)
           tool.setStatus(msg)
       elif len(tool.diffRecords) == 1:
           msg = str(len(tool.diffRecords)) + " difference found."
           print(msg)
           tool.setStatus(msg)
       else:
           msg = str(len(tool.diffRecords)) + " differences found."
           print(msg)
           tool.setStatus(msg)

       tool.diffRecords.reverse()

       # First traversal. Do not modify tool.diffRecords.
       for t, a1, a2, b1, b2 in tool.diffRecords:
           if t == "a":
               # Something that only exists on the right side.
               assert(a1 == a2)
               assert(b1 <= b2)
               i=b1
               while i<=b2:
                   rightData[i-1][1]="red" 
                   i += 1

           if t == "d":
               # Something that only exists on the left side.
               assert(b1 == b2)
               assert(a1 <= a2)
               i=a1
               while i <= a2:
                   leftData[i-1][1]="green"
                   i += 1

           if t == "c":
               # Something that exists on both side.
               assert(a1 <= a2)
               assert(b1 <= b2)
               i=a1
               while i <= a2:
                   leftData[i-1][1] = "blue"
                   i += 1
               i = b1
               while i <= b2:
                   rightData[i - 1][1]="blue"
                   i += 1

       for t, a1, a2, b1, b2 in tool.diffRecords:
           #print t,a1,a2,b1,b2
           if t == "a":
                # Something that only exists on the right side.
                assert(a1==a2)
                assert(b1<=b2)
                i=b1
                while i<=b2:
                    leftData.insert(a1,["\n","red"])
                    i=i+1
           if t == "d":
                # Something that only exists on the left side.
                assert(b1==b2)
                assert(a1<=a2)
                i=a1
                while i<=a2:
                    rightData.insert(b1,["\n","green"])
                    i=i+1
           if t == "c":
                # Something that changed between the two sides.
                assert(a1 <= a2)
                assert(b1 <= b2)
                if a2-a1 < b2-b1:
                    i = b1 + a2 - a1
                    while i < b2:
                        leftData.insert(a2, ["\n", "blue"])
                        i = i + 1
                elif a2 - a1 > b2 - b1:
                    i = a1 + b2 - b1
                    while i < a2:
                        rightData.insert(b2, ["\n", "blue"])
                        i = i + 1

       tool.diffRecords.reverse()   # for canvasChanged in ascending order

       lineNumber=1
       oldTag=None
       a=None
       b=None
       for x, t in leftData + [("Dummy",None)]:
           if t != oldTag:
               if a is not None:
                   b = lineNumber
                   tool.navigationList.append((a,b,oldTag))
               if t is None:
                   a = None
               else:
                   a = lineNumber
           oldTag = t
           lineNumber += 1

       tool.totalLines = lineNumber - 2 

       tool.linesLabel.config(text = "Total lines: %d" % tool.totalLines)

       tool.leftText.tag_config("red", background="pink")
       tool.leftText.tag_config("green", background="lightgreen")
       tool.leftText.tag_config("blue", background="lightblue")
       tool.leftText.tag_config("highlight", background="black",foreground="white")
       # diffchar tag must be created after highlight tag in order to have priority
       # (still be visible when highlighted)
       tool.leftText.tag_config("bluediffchar",
               background="red",
               foreground="white",
               relief=tkinter.GROOVE)
       tool.leftText.tag_raise(tkinter.SEL)  # SEL overrides all other tags
       tool.leftText.tag_config(tkinter.SEL,background="black",foreground="white")

       tool.rightText.tag_config("red",background="pink")
       tool.rightText.tag_config("green",background="lightgreen")
       tool.rightText.tag_config("blue",background="lightblue")
       tool.rightText.tag_config("highlight",background="black",foreground="white")
       # diffchar tag must be created after highlight tag in order to have priority
       tool.rightText.tag_config("bluediffchar",
               background="red",
               foreground="white",
               relief=tkinter.GROOVE)
       tool.rightText.tag_raise(tkinter.SEL)  # SEL overrides all other tags
       tool.rightText.tag_config(tkinter.SEL,background="black",foreground="white")

       assert(len(leftData)==tool.totalLines)
       assert(len(rightData)==tool.totalLines)

       lineNumber=0
       while lineNumber<tool.totalLines:
           leftLine,leftTag=leftData[lineNumber]
           rightLine,rightTag=rightData[lineNumber]
           assert(leftTag==rightTag)
           if (leftTag == "blue" and 
               leftLine != "" and leftLine != "\n" and
               rightLine != "" and rightLine != "\n"):
               xdleft,ydleft,xdright,ydright = onelinediff(leftLine,rightLine)
               # xdleft points now to the first different character of the line
               # ydleft points to first different character from the end

               tool.leftText.insert(tkinter.END,leftLine[:xdleft],"blue")
               tool.leftText.insert(tkinter.END,leftLine[xdleft:len(leftLine)-ydleft],"bluediffchar")
               tool.leftText.insert(tkinter.END,leftLine[len(leftLine)-ydleft:],"blue")
               tool.rightText.insert(tkinter.END,rightLine[:xdright],"blue")
               tool.rightText.insert(tkinter.END,rightLine[xdright:len(rightLine)-ydright],"bluediffchar")
               tool.rightText.insert(tkinter.END,rightLine[len(rightLine)-ydright:],"blue")
           else:
               tool.leftText.insert(tkinter.END,leftLine,leftTag)
               tool.rightText.insert(tkinter.END,rightLine,rightTag)
           lineNumber=lineNumber+1

       tool.navigateToIndex()
   except IOError as ex:
       exstr = str(ex)
       sys.stderr.write(exstr+"\n")
       MessageDialog(tool, "xdiff IO Error", exstr)
       sys.exit(1)
       
   try:
       tk.mainloop()
   except KeyboardInterrupt:
       pass
   



