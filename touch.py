#!/usr/bin/env python3
#
# touch.py - touch
#
# Make use of PATH and PATHEXT variable.
# PATHEXT has all the executable file extensions.
#

import sys, getopt
import os, os.path 

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "") 
    if arguments == []:
        print("touch - missing arguments")
        sys.exit(2)

    for filename in arguments:
        if os.path.exists(filename):
            print(filename, "already exists.")
        else:
            open(filename,"w").close()