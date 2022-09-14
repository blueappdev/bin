#!/usr/bin/env python
#
# bulkrename.py
#
# requires python 2.7

import re, os, sys

try:
    pattern = re.compile(sys.argv[1]);
    replace = sys.argv[2];
except IndexError:
    print 'usage: bulkrename search replace'
    print '    - replace the long prefix with a short prefix'
    print '      bulkrename "(Holiday Pictures 2008)(.*)" "Holi2008\\2"'
    print '    - reverses the first part of numbers with the second part of any characters'
    print '      bulkrename "^(\\d+)(.*?)\\.txt$" "\\2\\1.txt"'
    sys.exit()

filenames = os.listdir(os.getcwd())
    
for filename in filenames:
    if pattern.search(filename):
        newFilename = re.sub(pattern, replace, filename)
        try:
            print filename, "-->", newFilename
        except:
            print "Unable to preview " + filename + " --> " + newFilename

print "Please confirm y/n?"
if sys.stdin.readline().strip().lower() != "y":
    print "aborted"
    sys.exit()

for filename in filenames:
    if pattern.search(filename):
        newFilename = re.sub(pattern, replace, filename)
        try:
            os.rename(filename, newFilename)
        except:
            print "Unable to rename: " + filename + " --> " + newFilename
