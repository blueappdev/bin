#!/usr/bin/env python3
#
# rm.py - remove files
#

import sys, getopt, glob
import os, os.path 

def usage():
    print("rm - remove files (python version)")
    print("    -f force")
    print("    -r recursive")
            
if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "fr")
    if arguments == []:
        usage()
        sys.exit(2)
    
    for k, v in options:
        assert v == "", "unexpected option value"
        print("options not supported yet", k)
        sys.exit(2)

    for pattern in arguments:
        for filename in glob.glob(pattern):
            os.remove(filename)
               

   
    
    
