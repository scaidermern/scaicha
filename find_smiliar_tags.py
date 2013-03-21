#!/usr/bin/python
#
# parses the tag dump file from scaicha to find possibly misspelled tags
#

import difflib
import getopt
import sys
from itertools import combinations

def printUsage(name):
    print "usage:", name, "[OPTIONS] [FILES]"
    print "  -f      , --fast          fast mode with less accuracy"
    print "  -r <arg>, --ratio <arg>   minimum similarity ratio (0..1) (default: 0.9)"
    print "  -h      , --help          print this help and exit"
    print

if __name__ == '__main__':
    try:
        # get command line arguments
        opts, args = getopt.getopt(sys.argv[1:], "fr:h", ["fast", "ratio=", "help"])
    except getopt.GetoptError:
        printUsage(sys.argv[0])
        raise RuntimeError, "invalid argument specified"
    
    fast = False
    minRatio = 0.9
    for opt, arg in opts:
        if opt in ("-f", "--fast"):
            fast = True
        elif opt in ("-r", "--ratio"):
            try:
                minRatio = float(arg)
            except ValueError:
                raise RuntimeError, "ratio argument '" + arg + "' is not a float!"
        elif opt in ("-h", "--help"):
            printUsage(sys.argv[0])
            sys.exit(1)
    
    # all remaining arguments are files
    files = args
    if len(files) == 0:
        printUsage(sys.argv[0])
        raise RuntimeError, "no files specified!"
    
    # parse tag dumps
    tagSet = set()
    for file in files:
        print "parsing file", file
        file = open(file, "r")
        for line in file:
            line = line.rstrip("\n")
            tagSet.add(line.split("\t")[1])
        file.close()

    # compare each tag with each other one
    print "searching for similar tags (this will take some time)"
    for tag, otherTag in combinations(tagSet, 2):
        ratio = None
        if not fast:
            ratio = difflib.SequenceMatcher(None, tag, otherTag).ratio()
        else:
            ratio = difflib.SequenceMatcher(None, tag, otherTag).quick_ratio()
        if ratio > minRatio:
            print "'%s' and '%s' have a similarity ratio of %s" % (tag, otherTag, ratio)
    