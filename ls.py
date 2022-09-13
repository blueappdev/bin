#!/usr/bin/env python3
#
# ls.py - remove files
#

import sys, getopt, glob
import os, os.path 

def usage():
    print("ls - list files (python version)")
    print("    -l long form")

longForm = False

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "laf1r")
    if arguments == []:
        arguments = ['*']
    
    for k, v in options:
        if k == "-1":
            longForm = False
        elif k == "-l":
            longForm = True
        else:
            print("option not supported yet", k, v)
            sys.exit(2)

    for pattern in arguments:
        for filename in glob.glob(pattern):
            print(filename)
               

   
    
    
