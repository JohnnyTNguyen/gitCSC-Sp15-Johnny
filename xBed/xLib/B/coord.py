from itertools import imap
import time
import sys
import os
import pwd
import platform
import random

from math import log

def neighborhood(coordPivot = [0, 1, 0, 1, 0, 1, 0]):
    thisCmd = "B.coord.neighborhood"
    ABOUT = "\n".join("This command {} takes a binary coordinate such as 0101010 (here of",
                       "size L = 7) and returns a set of all ** adjacent coordinates **, i.e. the",
                       "coordinates with the Hamming distance of 1 from the input coordinate.",
                       "The size of this set is L.").format(thisCmd)
                       
    if coordPivot == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return
                           
    if coordPivot == "??":
        print ABOUT
        return
                       
    L = len(coordPivot)
    coordNeighbors = []

    for i in range(L):
        bit = coordPivot[i]
        if bit:
            coordPivot[i] = 0
        else:
            coordPivot[i] = 1
        coordAdj = str(coordPivot)
        coordNeighbors.append(coordAdj)

    print("coordPivot\n" + coordPivot + "\ncoordNeighbors\n" + coordNeighbors)
    return coordNeighbors

def distance(bstrL = [0, 1, 0, 1], bstrR = [1, 0, 0, 1]):
    thisCmd = "B.coord.distance"
    ABOUT = """This procedure takes two binary strings and returns
        the value of the Hamming distance between the strings.
        """
    if bstrL == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return

    if bstrL == "??":
        print ABOUT
        return
    
    L = len(bstrL)
    dist = 0
    if L != len(bstrR):
        print("ERROR ... unequal length strings: " + str(len(bstrL)) + " vs " + str(len(bstrR)))
        return
    for j in range(L):
        bL = bstrL[j]
        bR = bstrR[j]
        if bL != bR:
            dist += 1
    return dist    

def from_int(val = 31, maxBits = 5):
    thisCmd = "B.coord.from_int"
    ABOUT = """This procedure takes an integer and the length of the binary string that
        can represent this integer and returns a binary string that actually
        represents this integer.
        """
    
    if val == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return

    if val == "??":
        print ABOUT
        return
    
    intMax = int(pow(2, maxBits)) - 1
    bstr = []
    if val > intMax:
        print("\nERROR from {} ..."
          "maxBits={} cannot represent an integer={} \n").format(thisCmd, maxBits, val)
    elif val < 0:
        print("\nERROR from {} ... negative input value, val = {} \n").format(thisCmd, val)
    elif val > 0:
        nBits = int(log(val, 2.0))
        remainder = val
        for i in range(int(nBits), -1, -1):
            base = pow(2, i)
            quotient = remainder/base
            remainder = remainder % int(base)
            bstr.append(quotient)

    numZeros = maxBits - len(bstr)

    zeros = []
    for i in range(numZeros):
        zeros.append(0)

    return zeros + bstr

def rand(L = 41, weightFactor = None):
    thisCmd = "B.coord.rand"
    ABOUT = """This proc takes an integer L, and optionally a weightFactor > 0 and <= 1.
        By default, weightFactor = NA, and an unbiased binary coordinate of length L
        is returned. For weightFactor=0.5, a biased random coordinate of length L
        is returned: it will have  a random distribution of exactly L/2 'ones'
        for L even and (L+1)/2 'ones' for L odd.
        """
    
    if L == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return

    if L == "??":
        print ABOUT
        return
    
    coord = []
    if weightFactor == None:
        for i in range(L):
            coord.append(int(.5 + random.random()))
    return coord

def rank(bstr = [0, 0, 0, 1, 1, 0, 1]):
    thisCmd = "B.coord.rank"
    ABOUT = """This proc takes a binary coordinate as a string such as '010101' and
        returns its weight number as the number of 'ones', which can also be
        interpreted as the distance from '000000' or as 'the rank' of the
        coordinate in the Hasse graph with respect to its 'bottom' coordinate
        of all 'zeros'.
        """
    
    if bstr == "?":
        print("Valid query is '" + thisCmd + " ??'")
        return

    if bstr == "??":
        print ABOUT
    return bstr.count(1)

def string_vs_list(L = 32, Lpoints = 3, sampleSize = 1000, seedInit = 1215):
    thisCmd = "B.coord.string_vs_list"
    ABOUT = """
        Example:  {}  L   Lpoints    sampleSize  seedInit
                  {}  32  7          2000        1066
        
        The command {} implements an asympototic experiment to test
        runtime costs of decoding binary coordinates represented either as a binary
        string  or a binary list. There are 4 input parameters:
        the length of a binary coordinate L,
        the value of Lpoints (points in the asymptotic experiments)
        the value of sampleSize, and
        the value of seedInit.
        
        The experiment proceeds as follows:
        (1) creates  a refererence coordinate list of alternating 0's and 1's.
        (2) creates two coordinate samples as random permutations of coordRefList;
        one sample as a list of binary strings; the other as a list of binary lists.
        (3) decodes commponent values of each coordinate sample.
        (4) measures the total runtime of the two decoding operations for each L.
        """.format(thisCmd, thisCmd, thisCmd)
    if L == "??":
        print ABOUT
        return
    if L == "?":
        print "Valid query is " + thisCmd + "(\"?\")"
        return

    if L % 2:
        print "\nERROR from " + thisCmd + ":\nthe value of L=" + str(L) + " is expected to be even!\n"

    if seedInit == "":
        # initialize the RNG  with a random seed
        seedInit = 1e9 * random.random()
        random.seed(seedInit)
    elif isinstance(seedInit, int):
        # initialize the RNG  with a user-selected seed
        random.seed(seedInit)
    else:
        print "ERROR from " + thisCmd + ":\n.. only seedInit={} or seedInit=<int> are valid assignments, not -seedInit " + str(seedInit)
    L_list = []
    for points in range(1, Lpoints + 1):
        L_list.append(L*pow(2, points - 1))

    tableFile = thisCmd + "-" + str(sampleSize) + "-" + str(seedInit) + "-" + "asympTest.txt"

    tableLines = """# file = {} (an R-compatible file of labeled columns
# commandLine = {}({}, {}, {}, {})
# invoked on {}
# hostID = {}@{}-{}-{}
# compiler = python-{}
#
# seedInit = {}
# sampleSize = {}
#
#        	coordAsString\t\tcoordAsList
# coordSize\truntimeString\t\truntimeList\t\truntimeRatio
coordSize\truntimeString\t\truntimeList\t\truntimeRatio\n""".format(tableFile, thisCmd, L, Lpoints, sampleSize, seedInit, time.strftime("%a %b %d %H:%M:%S %Z %Y"), pwd.getpwuid(os.getuid())[0],
            os.uname()[1], platform.system(), os.uname()[2], ".".join(imap(str,sys.version_info[:3])), seedInit, sampleSize)
    for L in L_list:
        coordRefList = []
        for i in range(L):
            if i % 2:
                coordRefList.append(1)
            else:
                coordRefList.append(0)
        #print str(L) + "/" + str(coordRefList)
        runtimeList = 0.0
        runtimeString = 0.0

        for sample in range(1, sampleSize + 1):
            random.shuffle(coordRefList) #NOTE: In comparison to tcl version, this line actually shuffles the list
            coordString = ''.join(map(str, coordRefList))
            rankList = 0
            rankString = 0

            microSecs = time.time()

            for item in coordRefList:
                if item:
                    rankList += 1

            runtimeList = runtimeList + (time.time() - microSecs)

            microSecs = time.time()
    
            for i in range(L):
                item = int(coordString[i])
                if item:
                    rankString += 1
            
            runtimeString = runtimeString + (time.time() - microSecs)


            if rankList != rankString:
                print "ERROR from " + thisCmd + ":\n.. rank mismatch:rankList=" + str(rankList) + ", rankString=" + str(rankString) + "\n"
            runtimeRatio = runtimeString/runtimeList
        tableLines += (str(L) + "\t\t" + format(runtimeString, ".18f") + "\t" + format(runtimeList, ".18f") + "\t" + format(runtimeRatio, ".18f") + "\n")
    print "\n" + tableLines
    file_write(tableFile, tableLines)
    print ".. created file " + tableFile
    return

def file_write(fileName, data):
    try:
        f = file(fileName,'a')
        f.write(data)
        f.close()
    except IOError as e:
        sys.stderr.write("Error: {}\n".format(e.strerror))
        sys.exit(1)
