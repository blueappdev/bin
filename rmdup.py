#!/usr/bin/env python
#
# rmdup.py
#

import sys, getopt, glob
import os, os.path, filecmp

data = {}

def processFile(filename):
    fileSize = os.path.getsize(filename)
    #print "process", filename , fileSize
    if fileSize not in data:
        data[fileSize] = []
    data[fileSize].append(filename)

def processCandidates(candidates):
    assert len(candidates) >= 1
    if len(candidates) == 1:
        return
    if len(candidates) > 2:
        print "Only two candidates supported"
        return
    assert len(candidates) >= 2 
    filename1 = candidates[0]
    filename2 = candidates[1]
    assert filename1 != filename2
    print "check1"
    compareFlag = filecmp.cmp(filename1,filename2)
    print "check2"
    if compareFlag:
        if len(filename1) > len(filename2):
            filenameToDelete = filename1
        else:
            filenameToDelete = filename2
        print "Delete duplicate", filenameToDelete
        os.remove(filenameToDelete)
    

def processData():
    for candidates in data.itervalues(): 
        processCandidates(candidates)

def usage():
    print "rmdup - remove duplicate files"
            
if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:],"")
    if arguments == []:
        usage()
        sys.exit(2)
    for pattern in arguments:
        for filename in glob.glob(pattern):
            processFile(filename)
    processData()

    
    
