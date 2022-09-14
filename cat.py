#!/usr/bin/env python3
#
# cat.py - cat files
#

import sys, getopt, glob
import os, os.path 

class Tool():
    def usage(self):
        print("cat - cat files (python version)")
        print("    -n   number all output lines")
        
    def setDefaultConfiguration(self):
        self.lineNumberFlag = False

    def processCommandLine(self, commandLine):
        options, arguments = getopt.getopt(commandLine[1:], "n")
        self.setDefaultConfiguration()
        for k, v in options:
            if k == "-n":
                self.lineNumberFlag = True
            else:
                print("option not supported yet", k, v)
                sys.exit(2)
        self.processPatterns(arguments)
    
    def processPatterns(self, patterns):
        for pattern in patterns:
            self.processPattern(pattern)
            
    def processPattern(self, pattern):
        for filename in glob.glob(pattern):
            self.processFilename(filename)

    def processFilename(self, filename):
        stream = open(filename)
        lineNumber = 1
        for line in stream:
            if self.lineNumberFlag:
                print(str(lineNumber).rjust(6, " "), end = "  ")
            print(line, end = "")
            lineNumber += 1
        stream.close()


if __name__ == "__main__":
    Tool().processCommandLine(sys.argv)
