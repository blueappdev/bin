#!/usr/bin/env python3
#
# which.py - find files in path
#
# Make use of PATH and PATHEXT variable.
# PATHEXT has all the executable file extensions.
#

import sys, getopt
import os, os.path 

def usage():
    print("which.py - find files in path")

def splitEnvironmentVariable(environmentVariableName):
    return os.environ.get(environmentVariableName,"").lower().split(";")
    
if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "") # "fr"
    if arguments == []:
        usage()
        sys.exit(2)

    directories = splitEnvironmentVariable("PATH")
    extensions = splitEnvironmentVariable("PATHEXT")
    
    # also find files in the current directory
    directories = ["."] + directories  
    
    # also find files without extension
    extensions = [""] + extensions 
    
    #print "Extensions", extensions
    #print "PATH", directories
    
    counter = 0
    
    for filename in arguments:
        for directory in directories:
            for extension in extensions:
                f = os.path.join(directory, filename + extension)
                if os.path.exists(f):
                    print(f)
                    counter = counter + 1
                    
    if counter == 0:
        print('No file found.')
   

               

   
    
    
