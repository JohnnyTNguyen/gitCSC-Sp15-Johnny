from itertools import imap
import B.coord
import time
import sys
import os
import pwd
import platform
import random
import util
import core
from config import *
import getpass
from math import log
from pprint import pprint

def main(instanceDef, args = []):
    #-- begin ABOUT ---------------------------------------------------------------#
    thisCmd = "B.lightp.main"
    ABOUT = """
Proc {} takes a variable number of arguments: 'instanceDef' as the
required argument and a number of optional arguments (in any order).
To output the command line description of {}, invoke the command"

  B.lightp.info(1)

To read the instance and output the initialized data structures **only**,
invoke the command

  B.lightp.main("<instanceDef>",["-isInitOnly","\[none-or-any-other-options\]")

To read the instance and output results returned by the solver,
invoke the command

  B.lightp.main("<instanceDef>", otherArgs)

To output the command line documentation of the encapsulated/executable
version of {}

  ../xBin/B.lightp
""".format(thisCmd, thisCmd, thisCmd)
    if instanceDef == "??":
        print ABOUT
        return
    elif instanceDef == "?":
        print "Valid query is '{} ??'".format(thisCmd)
        return
    
    #info global variables
    global all_info
    global all_valu
    global aV
    #instance global variables
    global aStruc
    #solver global variables
    global aCoordHash0
    global aWalkProbed
    
    #!! (1) Phase 1: query about commandLine **OR** initialize all variables
    if instanceDef == "?":
        # read solver domain table and return query about commandLine
        info(1, all_info("infoVariablesFile"))
        return
    else:
        # variable initialization
        rList = init(instanceDef, args)

    if rList is None:
        return
    elif aV["isInitOnly"]:
        print ("\n{}"
            "\n.. completed initialization of all variables,"
            "\n   exiting the solver since option -{} has been asserted."
            "\n{}\n".format("-"*78,aV["isInitOnly"],"-"*78))
        print "targetReached coordInit valueInit = {}\n".format(rList)
        for key, value in aV.items():
            print "aV({}) = {}".format(key,value)
        print
        for i in range(len(aStruc)):
            print "aStruc[{}] = {}".format(i, aStruc[i])
        print
        for key, value in aCoordHash0.items():
            print "aCoordHash0({}) = {}".format(key,value)
        print
        for key, value in aWalkProbed.items():
            print "aWalkProbed({}) = {}".format(key,value)
        return
    else:
        print("\n{}"
            "\n.. completed initialization of all variables,"
            "\n   proceeding with the search under solverID = B.lightp.{}"
            "\n{}\n").format("-"*78,aV["solverID"].__name__,"-"*78)

    # (2) Phase 2: proceed with the combinatorial search
    if aV["solverMethod"] == "saw":
        aV["solverID"] = saw
    else:
        print "\nERROR from {}:\nsolverMethod = {} is not implemented\n".format(thisCmd, aV["solverMethod"])
        return
    print "#    Proceeding with the search under solverID = B.lightp.{}".format(aV["solverID"].__name__)
    print "#"*78
    aV["solverID"]()
    
    stdout()
    if aV["isWalkTables"]:
        print "TODO: walk.tables method"
    return

def info(isQuery=0, infoVariablesFile = "../xLib/B.lightp.info_variables.txt"):
    thisCmd = "B.lightp.info"
    ABOUT = """
        This proc takes a variable 'isQuery' and the hard-wired path to file
        infoVariablesFile *info_variables.txt.
        
        if isQuery == 0    then {} ONLY reads infoVariablesFile and
        initializes global arrays 'all_info' and 'all_valu'
        
        if isQuery == 1    then $thisCmd initializes the global arrays
        'all_info' and 'all_valu' and then outputs to stdout
        the complete information about the command line for
        B.lightp.main. The information about the command line
        is auto-generated within {} from the
        tabulated data which is read from infoVariablesFile
        defined above.
        
        if isQuery == ??  then {} responds to stdout with information
        about all three case of valid arguments.
        
        B.lightp.main ??   (under python)
        or
        ../xBin/B.lightpP  (under bash)
        """.format( thisCmd, thisCmd, thisCmd )
    if isQuery == "??":
        print ABOUT
        return
    elif isQuery == "?":
        print "Valid query is '{} ??'".format(thisCmd)
        return

    #info global variables
    global all_info
    global all_valu
    global aV

    # read *.info_variables.txt for this solver domain
    rList = util.table_info_variables(infoVariablesFile)
    sandboxName = all_info["sandboxName"]
    sandboxPath = all_info["sandboxPath"]
    all_info = rList[0]
    all_valu = rList[1]
    all_info["sandboxName"] = sandboxName
    all_info["sandboxPath"] = sandboxPath
    all_info["infoVariablesFile"] = infoVariablesFile

    if not isQuery:
        return (all_info, all_valu)
    elif isQuery != 1:
        print ("\nERROR from {}: incorrect arguement value!"
               "\nFor more information, use the command B.lightp.info ??\n")


    # Preferred order of optional commandLine arguements
    optInfoList = [ "runtimeLmt", "cntProbeLmt", "cntRestartLmt", 
            "walkLengthLmt", "seedInit", "coordInit", "valueInit",
            "valueTarget", "valueTol", "walkSegmLmt",
            "walkSegmCoef", "isSimple", "writeVar" ]

    #TODO: SJDFASKDFJSDKFAJSDFKJ FIX THIS COMMENT
    print "\n".join([
        "USAGE:\n",
        "under TkCon shell (which has sourced ../xLib/all_python.py",
        "\tB.lightp.main instanceFile [optional_arguments]",
        "",
        "under bash, invoking the 'tcl executable B.lightpT' which sources" +
        " libraries directly",
        "\t../xBin/B.lightpT instanceFile [optional_arguments]",
        "",
        "under bash, invoking the 'python executable B.lightpP' which sources" +
        " libraries directly",
        "\t../xBin/B.lightpP instanceFile [optional_arguments]",
        "",
        "under bash, invoking the 'compiled C++ code as a binary B.lightpX",
        "\t../xBin/B.lightpX instanceFile [optional_arguments]",
        "",
        "DESCRIPTION:",
        "B.lightp.main, B.lightpT, B.lightpP, or B.lightpX take one REQUIRED argument",
        "and a number of OPTIONAL arguments in any order. The most" +
        " significant parameter,",
        "extracted from the instanceDef is",
        "\tnDim ... coordinate size,",
        "\t\t\ti.e. the number of variables (columns in the square matrix)",
        "Here is a complete list of pairs 'name defaultValue', with short",
        "in-line descriptions:"
    ])

    # create nameList and valuelist
    for name in optInfoList:
        value = all_valu[name]
        nameList = []
        valueList = []
        nameList.append(name)
        valueList.append(value)
        # pad with blank spaces
        for i in range(len(all_info[name])):
            nameList.append(" "*len(name))
            valueList.append(" "*len(value))

        optArgData = [(nameList[i], valueList[i], all_info[name][i]) for i in range(len(all_info[name]))]
        for (nam, val, descr) in optArgData:
            cnt = 17 - len(nam)
            space1 = " "*cnt
            cnt = 12 - len(val)
            space2 = " "*cnt
            if len(nam) > 0 and nam.strip():
                # prefix with -
                nam1 = "-"+nam
            else:
                nam1 = " "+nam

            print "\t{}{}{}{}\t{}".format(nam1,space1,val,space2,descr)

    print "\n".join([
        "\nDETAILS:",
        "This solver reads an instance of the 'linear ordering problem in a " +
        "matrix format",
        "and returns a column/row ordering that minimizes the negative sum " +
        "of matrix",
        "elements above the diagonal. The example below shows an instance " +
        "of such a matrix",
        "with sum = -8 under its 'natural order', and an instance under an " +
        "optimal",
        "permutation of 3,1,4,2 with a sum of -13. For this matrix, there " +
        "are two more",
        "such optimal permutations: 2,3,1,4 and 4,2,3,1.",
        "",
        "natural order   under permutation",
        "  1,2,3,4          3,1,4,2",
        "  sum = -8         sum = -13",
        "------------    ------------",
        "4               4           ",
        "  0 0 0 5         0 4 1 1",
        "  1 0 2 0         0 0 5 0",
        "  4 1 0 1         1 3 0 2",
        "  3 2 1 0         2 1 0 0"
    ])

    return
    """
    #-- begin ABOUT ---------------------------------------------------------------#
    thisCmd = "B_lightp.info"
    ABOUT = "\n".join(["This proc takes a variable 'isQuery' and the hard-wired path to file",
                        "infoVariablesFile *info_variables.txt.\n",
                        "  if isQuery == 0    then $thisCmd ONLY reads infoVariablesFile and",
                        "initializes global arrays 'all_info' and 'all_valu'\n",
                        "  if isQuery == 1    then $thisCmd initializes the global arrays",
                        "'all_info' and 'all_valu' and then outputs to stdout",
                        "the complete information about the command line for",
                        "B.lightp.main. The information about the command line",
                        "is auto-generated within $thisCmd from the",
                        "tabulated data which is read from infoVariablesFile",
                        "defined above.\n",
                        "   if isQuery == ??  then $thisCmd responds to stdout with information",
                        "about all three case of valid arguments.\n",
                        "            B.lightp.main ??   (under tclsh)",
                        "       or",
                        "            ../xBin/B.lightpT  (under bash)"])
    if isQuery == "??":
        print(ABOUT)
        return
    if isQuery == "?":
        print("Valid query is " + thisCmd + " ??'")
        return
    #-- end   ABOUT ---------------------------------------------------------------#

    # read the *.info_variables.txt for this solver domain
    rList = util.table_info_variables(infoVariablesFile)
    all_info = rList[0]
    all_valu = rList[1]

    if not isQuery:
        return

    # the preferred order (for user query) of optional commandLine argument names
    optInfoList = ["runtimeLmt", "cntProbeLmt", "cntRestartLmt", "walkLengthLmt", "seedInit", "coordInit", "valueTol", "walkSegmLmt", "walkSegmCoef", "isSimple", "isInitOnly", "isWalkTables", "writeVar"]

    ### Now, respond to a query from the user
    print("\n".join([
        "Usage:",
        "under TkCon shell (which has sourced ../xLib/all_tcl):",
        "B_lightp.main instanceDef [optional_arguments]",
        "\n",
        "under bash, invoking the tcl executable B.lightpT' which sources libraries directly",
        "../xBin/B_lightpT instanceDef [optional_arguments]",
        "\n",
        "under bash, invoking the 'python executable B_lightpP' which sources libraries directly",
        "../xBin/B_lightpP instanceDef [optional_arguments]",
        "\n",
        "under bash, invoking the 'compile C++ code as a binary B.lightpX'",
        " ../xBin/B.lightpX  instanceDef [optional_arguments]",
        "\n",
        "EXAMPLES:",
        "B.lightp.main     ../xBenchm/lightp/i-6-a-0.txt -isInitOnly",
        "B.lightp.main     ../xBenchm/lightp/i-6-a-0.txt -seedInit 1215",
        "../xBin/B.lightpT ../xBenchm/lightp/i-6-a-0.txt -seedInit 1215 -coordInit 010110",
        "../xBin/B.lightpP ../xBenchm/lightp/i-6-a-0.txt -seedInit 1215 -coordInit [0, 1, 0, 1, 1, 0]",
        "../xBin/B.lightpX ../xBenchm/lightp/i-6-a-0.txt -seedInit 1215 -runtimeLmt 5",
        "\n",
        "DESCRIPTION:",
        "B.lightp.main, B.lightpT, B.lightpP, or B.lightpX take one REQUIRED argument",
        "\n",
        "    instanceDef  (a filePath with an extension .txt)",
        "\n",
        "and a number of OPTIONAL arguments in any order.",
        "\n",
        "Here is a complete list of 'name defaultValue' options, with short",
        "in-line descriptions for each option:"]))

    # create nameList and valueList with
    for name in optInfoList:
        value = all_valu[name]
        # create nameList and valuList padded with blank space
        nameList = []
        valueList = []
        nameList.append(name)
        valueList.append(value)
        for i in range(len(all_info[name])):
            nameList.append(" "*len(name))
            valueList.append(" "*len(value))

        optArgData = [(nameList[i], valueList[i], all_info[name][i]) for i in range(len(all_info[name]))]
        for (nam, val, descr) in optArgData:
            cnt = 17 - len(nam)
            space1 = " "*cnt
            cnt = 12 - len(val)
            space2 = " "*cnt
            if len(nam) > 0 and nam.strip():
                # prefix with -
                nam1 = "-"+nam
            else:
                nam1 = " "+nam

            print "\t{}{}{}{}\t{}".format(nam1, space1, val, space2, descr)
            
        print("\n".join([
            "\nDETAILS:",
            "This solver reads from a file an instance of the 'lights-out puzzle problem'",
            "defined by a binary string which can be of length 4=2*2, 6=2*3, 9=3*3,",
            "12=3*4, 16=4*4, 20=4*5, 25=5*5, 30=5*6, 36=6*6, 42=6*7, etc. This string",
            "represents lights that are 'on' in a rectangular matrix of size L=M*N.",
            "The solver returns a binary solution string of length L that minimizes",
            "the number of lights that could be turned off for the given instance.",
            "For the instance shown below, there exist a single solution only!\n",
            "instanceInit     solutionBest",
            " 001001011         001101001",
            "lights-on= 4     lights-on= 0",
            "------------     ------------",
            "  0 0 1            0 0 0",
            "  0 0 1            0 0 0",
            "  0 1 1            0 0 0"]))
        return
    """

def init( instanceDef, args = [] ):
    thisCmd = "B.lightp.init"
    mainProc = "B.lightp.main"
    #TODO: sdjfsalfjaldfjlak fix this comment too
    ABOUT = "Procedure " + thisCmd + "takes a variable number of arguments:\ninstanceDef as required argument and args. It then  decodes values of args and\ninitializes all variables under global arrays. $thisCmd is invoked by\nB.lightp.main; for details about the command-line structure, query B.lightp.main ??\nAlso, $thisCmd explicitly returns values of 'targetReached valueInit coordInit'."
    
    if instanceDef == "??":
        print ABOUT
        return
    if instanceDef == "?":
        print "Valid query is '{} ?? '".format(thisCmd)
        return
    """
    argsOptions = args

    # read the solver domain table
    rList = info(0, all_info[infoVariablesFile])
    all_info = rList[0]
    all_valu = rList[1]

    #!! (0A) Phase 0A: initialize all NEW global arrays
    for name in all_info['globalArrays'][0]:
        # NOTE: array all_info have been initialized ALREADY!!
        if name != "all_info" and name != "all_valu":
            name = []
            
    # the check on llength of argsOptions when invoked under bash!!
    if len(argsOptions) == 1:
        argsOptions = argsOptions[0]
    print("# ** from: " + thisCmd + ":\n\# instanceDef=" + str(instanceDef) + "\n\# argsOptions=" + str(argsOptions))

    #!! (0B) Phase 0B: extract variable groups from array all_valu (created by proc B.lightp.info)  
    for name in all_valu:
        val = all_valu[name]

        if val == "required":
            namesRequired.append(name)
        elif val == "internal":
            namesInternal.append(name)
        elif val == "FALSE":
            namesOptionalBool.append(name)
            if not aV.has_key(name):
                aV[name] = val
        #print(".. after initializing aV from all_value array")
        #pprint(aV)
    #!! (1) Phase 1: initialize the REQUIRED commandLine variables the global array aV, 
    #including variables derived from instanceDef in the infoSolutionsFile
    aV['instanceDef'] = instanceDef# here, instanceDef is the name of the instance
    #!! #** timing starts ***
    microSecs = time.time()
    # read infoSolutionsFile for this instance  
    infoSolutionsFile.append(all_info['sandboxName'] + ".info_solutions.txt")
    infoSolutions = all_info['sandboxPath'] + "xBenchlightp" + infoSolutionsFile
            
    microSecs = time.time() - microSecs
    """
    # info global variables
    global all_info
    global all_valu
    global aV
    # instance global variables 
    global aStruc
    # solver global variables
    global aCoord0
    global aWalkProbed
    global aValueBest

    """
    global aHashTmp
    global aHashNeighb
    global aHashWalk
    global aWalk
    global aWalkProbed
    global aWalkBest
    global aAdjacent
    """
    argsOptions = args

    rList = info(0, all_info["infoVariablesFile"])
    all_info = rList[0]
    all_valu = rList[1]

    # (0A) Phase 0A: initialize global variables
    aV = {}
    aStruc = {}
    aCoord0 = {}
    aWalkProbed = {}

    print "\n".join([
        "# ** from: {}:".format(thisCmd),
        "# instanceDef={}".format(instanceDef),
        "# argsOptions={}".format(argsOptions)
        ])

    # (0B) Phase 0B: extract variable groups from all_valu
    namesRequired = []
    namesInternal = []
    namesOptionalBool = []
    namesOptional = []
    for name in all_valu.keys():
    
        val = all_valu[name]
    
        if val == "required":
            namesRequired.append(name)
        elif val == "internal":
            namesInternal.append(name)
            aV[name] = None
        elif val == "FALSE":
            namesOptionalBool.append(name)
            aV[name] = False 
        elif val == "TRUE":
            namesOptionalBool.append(name)
            aV[name] = True
        else:
            namesOptional.append(name)
            try:
                aV[name] = float(val)
            except:
                aV[name] = val
  
    # (1) Phase 1: initialize required commandline variables
    aV["instanceDef"] = instanceDef
    
    # Timing
    microSecs = time.time()
    
    infoSolutionsDir = os.path.dirname(os.path.realpath(aV["instanceDef"]))
    infoSolutionsFile = all_info["sandboxName"] + ".info_solutions.txt"
    infoSolutionsFile = "/".join([all_info["sandboxPath"], "xBenchm", "lightp",
        infoSolutionsFile])
    aV["infoSolutionsFile"] = infoSolutionsFile

    if not os.path.isfile(infoSolutionsFile):
        print "\nERROR from {}:\nfile {} is missing!\n".format(thisCmd, infoSolutionsFile)
        return
    rList = core.file_read(infoSolutionsFile).splitlines()
    rList.pop()
    rListTmp = []
    for line in rList:
        if len(line) > 0:
        # print line
            firstChar = line[0]
            if firstChar != "#":
                rListTmp.append(line)
    isFound = False
    for line in rListTmp:
        line = line.split()
        varName = line[0]
        if varName == aV["instanceDef"]:
            aV["instanceInit"] = int(line[1])
            aV["valueTarget"] = line[2]
            aV["isProven"] = line[3]
            aV["nDim"] = len(str(aV["instanceInit"]))
            try:
                aV["isProven"] = int(line[2].strip('-'))
            except:
                aV["isProven"] = False
            isFound = True
        if isFound:
            break
    if not isFound:
        print ("\nERROR from {}:"
               "\n .. instance {} was not found in file"
               "\n     {}\n".format(thisCmd, aV["instanceDef"], infoSolutionsFile))
        return
    #end timing
    microSecs = time.time() - microSecs

    aV["runtimeRead"] = microSecs
    aV["infoSolutionsFile"] = infoSolutionsFile
    aV["commandName"] = all_info["sandboxName"] + ".main"
    aV["commandLine"] = "{} {} {}".format(aV["commandName"] , instanceDef , argsOptions)
    aV["valueTarget"] = int(aV["valueTarget"]) * (1 - aV["valueTol"])

    # (2A) Phase 2A: initialize optional command line variables
    if len(argsOptions) > 0:
        tmpList = argsOptions
        while len(tmpList) > 0:
            name = tmpList[0].strip("-")
            if name in namesOptional:
                try:
                    aV[name] = float(tmpList[1])
                except:
                    aV[name] = tmpList[1]
                tmpList = tmpList[2:]
            elif name in namesOptionalBool:
                aV[name] = True
                tmpList = tmpList[1:]
            elif not name:
                print ("\nERROR from {}:"
                       "\n.. option name {} is not either of two lists below:"
                       "\n{}"
                       "\n\nor\n"
                       "\n{}".format(thisCmd, name, namesOptional, namesOptionalBool))
                return
            else:
                aV[name] = int(tmpList[1])
                tmpList = tmpList[2:]

    # (2B) Phase 2B: continue to initialize the optional command line variables
    # aV["seedInit"] needs to be initialized first
    if aV["seedInit"] == "NA":
        # initialize RNG with random seed
        aV["seedInit" ] = 1e9 * random.random()
        random.seed(aV["seedInit"])
    else:
        # initialize RNG with user provided seed
        try:
            aV["seedInit"] = int(aV["seedInit"])
            random.seed(aV["seedInit"])
        except:
            print ("ERROR from {}:"
                    ".. only -seedInit NA or -ssedInit <int> are valid assignments,"
                    "not -seedInit {}\n".format(thisCmd, aV['seedInit']))
            return
    # initialize random binary coordinate
    if aV["coordInit"] == None:
        # generate a random permutation coordinate
        aV["coordInit"] = B.coord.rand(aV["nDim"])
        aV['rankInit'] = B.coord.rank(aV["coordInit"])
    else:
        # check if user provided coordInit is the valid length
        aV["coordInit"] = [int(c) for c in aV["coordInit"].split(",")]
        if len(aV["coordInit"]) != aV["nDim"]:
            print ("\nERROR from {}:"
                "\nThe binary coordinate is of length {},"
                "not the expected length {}\n").format(thisCmd, aV["coordInit"], aV["nDim"])
            return
        aV["rankInit"] = B.coord.rank(aV["coordInit"])
        """
        if False:
            if aV["walkIntervalLmt"] == "NA" and aV["walkIntervalCoef"] != "NA":
                try:
                    walkIntervalCoef = float(aV["walkIntervalCoef"])
                    if walkIntevalCoef > 0.:
                        aV["walkIntervalLmt"] = int(walkIntervalCoef * aV["nDim"])
                        aV["walkIntervalCoef"] = walkIntervalCoef
                except:
                    sys.stderr.write(("\nERROR from {}:"
                                      "The walkIntervalCoef can only be assigned a value of NA"
                                      "or a positive number, not {} \n".format(thisCmd, aV["walkIntervalCoef"])))
                    sys.exit(1)
        elif aV["walkIntervalLmt"] != "NA" and aV["walkIntervalCoef"] == "NA":
            try:
                walkIntervalLmt = int(aV["walkIntervalLmt"])
                if walkIntervalLmt > 0:
                    aV["walkIntervalLmt"] = walkIntervalLmt
            except:
                sys.stderr.write(("\nERROR from {}:"
                                  "The walkIntervalLmt can only be assigned a value of NA"
                                  "or a positive number, not {} \n".format(thisCmd, aV["walkIntervalLmt"])))
                sys.exit(1)
        elif aV["walkIntervalLmt"] != "NA" and aV["walkIntervalCoef"] != "NA":
            sys.stderr.write(("ERROR from {}:"
                              "The walkIntervalLmt and walkIntervalCoef can only be assigned"
                              "pairwise values of\n(NA NA) (default) (NA double) or (integer NA)"
                              "not ({} {})\n".format(thisCmd, aV["walkIntervalLmt"], aV["walkIntervalCoef"])))
            sys.exit(1)
    """

    if aV["walkSegmLmt"] == "NA" and aV["walkSegmCoef"] != "NA":
        try:
            walkSegmCoef = float(aV["walkSegmCoef"])
            if walkIntevalCoef > 0.:
                aV["walkSegmLmt"] = int(walkSegmCoef * aV["nDim"])
                aV["walkSegmCoef"] = walkSegmCoef
        except:
            print ("\nERROR from {}:"
                    "The walkSegmCoef can only be assigned a value of NA"
                    "or a positive number, not {} \n".format(thisCmd, aV["walkSegmCoef"]))
            return
    elif aV["walkSegmLmt"] != "NA" and aV["walkSegmCoef"] == "NA":
        try:
            walkSegmLmt = int(aV["walkSegmLmt"])
            if walkSegmLmt > 0:
                aV["walkSegmLmt"] = walkSegmLmt
        except:
            print ("\nERROR from {}:"
                    "The walkSegmLmt can only be assigned a value of NA"
                    "or a positive number, not {} \n").format(thisCmd, aV["walkSegmLmt"])
            return
    elif aV["walkSegmLmt"] != "NA" and aV["walkSegmCoef"] != "NA":
        print ("ERROR from {}:"
                "The walkSegmLmt and walkSegmCoef can only be assigned"
                "pairwise values of\n(NA NA) (default) (NA double) or (integer NA)"
                "not ({} {})\n").format(thisCmd, aV["walkSegmLmt"], aV["walkSegmCoef"])
        return

    # (3A) Phase 3A: directly initialize the remaining internal variables
    aV["coordType"] = "B"
    aV["functionDomain"] = "B.lightp"
    aV["functionID"] = "lightp"

    # define solverID
    if aV["solverMethod"] == "ant" and aV["isSimple"]:
        aV["solverID"] = "ant_saw_simple"
    elif aV["solverMethod"] == "ant":
        aV["solverID"] = "ant_saw"
    elif aV["solverMethod"] == "bee":
        aV["solverID"] = "bee_saw"
    elif aV["solverMethod"] == "rw" and not aV["notSAW"]:
        aV["solverID"] = "rw_saw"
    elif aV["solverMethod"] == "rw" and aV["notSAW"]:
        aV["solverID"] = "rw"
    elif aV["solverMethod"] == "sa" and not aV["notSAW"]:
        aV["solverID"] = "sa_saw"
    elif aV["solverMethod"] == "sa" and aV["notSAW"]:
        aV["solverID"] = "sa"
    else:
        aV["solverID"] = saw

    # Time stamp (14-digit GMT formatting)
    aV["solverVersion"] = time.strftime("%Y %m %d %H:%M:%S")
    aV["timeStamp"] =  time.strftime("%Y%m%d%H%M%S")
    aV["dateLine"] = time.strftime("%a %b %d %H:%M:%S %Z %Y") 
    aV["hostID"] = "{}@{}-{}-{}".format(pwd.getpwuid(os.getuid())[0],
            os.uname()[1], platform.system(), os.uname()[2])
    aV["compiler"] = "python-"+".".join(imap(str,sys.version_info[:3]))

    # find aV["valueInit"] by doing the first probe for function value
    # Timing
    microSecs = time.time()
    rList = patterns(aV["instanceInit"])
    aV["M"] = rList[0]
    aV["N"] = rList[1]
    aStruc = rList[2]
    # Timing
    microSecs = time.time()

    aV["valueInit"] = f(aV["coordInit"])
    # end timing
    microSecs = time.time() - microSecs

    # initialize associated variables for initial probe
    aV["runtime"] = microSecs
    aV["cntProbe"] = 1
    aV["cntStep"] = 0
    aV["coordPivot"] = aV["coordInit"]
    aV["coordBest"] = aV["coordInit"]
    aV["valuePivot"] = aV["valueInit"]
    aV["valueBest"] = aV["valueInit"]
    aCoord0= {}
    aCoord0[tuple(aV["coordInit"])] = []

    # (4) Phase 4: check if valueTarget has been reached, return to main if > 0
    if aV["valueInit"] == aV["valueTarget"]:
        aV["targetReached"] = 1
    elif aV["valueInit"] < aV["valueTarget"]:
        aV["targetReached"] = 2
    else:
        aV["targetReached"] = 0

    # (5) Phase 5: complete initialization of aV before the first step
    #aHashWalk[tuple(aV["coordInit"])] = []
    aV["isCensored"] = 0
    aV["cntRestart"] = 0
    aV["walkLength"] = aV["cntStep"]
    aV["neighbSize"] = aV["nDim"] - 1
        #if aV["neighbDist"] == 1:
#aV["neighbSize"] = aV["nDim"] - 1
#else:
#aV["neighbSize"] = "dynamic"

    # (6) Phase 6: initialize special arrays that can be selected w/ arguments
    #       from command line
    if aV["writeVar"] >= 4:
        aV["isSimple"] = 1
    #aValueBest[aV["valueInit"]] = [0,0,aV["coordInit"]]
    #aWalkBest[aV["valueInit"]] = [0,0,aV["coordInit"],0,0]

    #aWalk[aV["cntStep"]] = "{} {} {} {} {} {}".format(aV["cntStep"], aV["cntRestart"], aV["coordPivot"], aV["valuePivot"], aV["neighbSize"], aV["cntProbe"])

    isPivot = 1
    aV["rankPivot"] = B.coord.rank(aV["coordPivot"])
    aWalkProbed[(aV["walkLength"],0)] = (aV["walkLength"], aV["cntRestart"],
        aV["coordPivot"], aV["valuePivot"], aV["rankPivot"], isPivot,
        aV["neighbSize"], aV["cntProbe"])

    # (7) Phase 7: verify that all variables under aV have been initialized in
    #       solverDomain table all_info["infoVariablesFile"]
    errorItems = []
    errorLines = []
    for name in aV.keys():
        if name not in all_valu:
            errorLines.append( ("{} -- this variable is missing from the solver"
                " domain table in the file {}\n".format(name, all_info["infoVariablesFile"])))
            errorItems.append(name)
    if len(errorItems) > 0:
        print "\nWarning from {}\n{}".format(thisCmd, errorLines)
        print "Missing variables\n{}\n".format(errorItems)

    # (8) Phase 8: check whether coordInit caused targetReached to be > 1
    if aV["targetReached"] > 0:
        print "# BINGO: valueTarget has been reached or exceeded with coordInit"
        stdout(withWarning=1)
        return

    # (9) Phase 9: write to stdout based on writeVar
    if aV["writeVar"] == 1:
        print "\n** Final values of initialized variables (array aV) **"
        print aV
        print "\n** Values associated with instance array aStruc **"
        print aStruc
        print "\n** as reported on {}, returning".format("@TODO: TIME STAMP")
        print "targetReached\tvalueInit\tcoordInit"

    #result = "{} {} {}".format(aV["targetReached"], aV["valueInit"], aV["coordInit"])
    result = (aV["targetReached"], aV["valueInit"], aV["coordInit"])
    return result
     
def saw_pivot_simple(coordPiv = [1, 1, 1, 1, 0, 1], valuePiv = 3):
    #-- begin ABOUT ---------------------------------------------------------------#
    thisCmd = "saw_pivot_simple"
    ABOUT = "This procedure takes a pivot coordinate/value, probes the distance=1 neighborhood of a 'light-out puzzle' (lightp), subject to the constraints of a SAW (self-avoiding walk) -- i.e. the best coord/value it returns has not been et selected as the pivot for the next step. Neighborhood size of 0 signifies that the next step of a SAW is blocked. This implementation is 'simple', i.e. for each pivot coordinate or length L, there are up to L explicit probes of the function f"
    if coordPiv == "??":
        print ABOUT
        return
    if coordPiv == "?":
        print "Valid query is '" + thisCmd + " ??'"
        return
    #-- end   ABOUT ---------------------------------------------------------------#
    coordBest = None
    valueBest = sys.maxint
    valueProbedList = []
    coordBestList = []
    neighbSize = 0
    coordProbedList = []
    aV['cntProbe'] = 0

    # We take coordPivot and flip the bit from left-to-right,
    # while also extracting neighbor with local valueBest.
    # To make this selection unbiased, we visit neighbors
    # in random order by first permuting aV(varList).
    # NOTE: To maintain a self-avoiding walk, the neighborhood
    # is defined only for coordinates not already used in the walk.

    if aV['writeVar'] == 3:
        distance = 0
        rank = B.coord.rank(coordPiv)
        rowLines = "\nA trace from " + thisCmd + ":\nEvaluating neighbors of coordPivot=" + str(coordPiv) + "\ncntProbe\tIdx\tcoordPivot\tvalPivot\tcoordAdj\tvalAdj\tdist\trank\n~\t~\t" + str(coordPiv) + "\t" + str(valuePiv) + "\t~\t~\t" + str(distance) + "\t" + str(rank) + "\n"
        varList = aV['varList']
    else:
        varList = aV['varList']
        shuffle(varList)
        print("cp:" + str(coordPiv))
    for var in varList:
        i = var - 1
        coordAdj = list(coordPiv)
        if coordAdj[i]:
            coordAdj[i] = 0
        else:
            coordAdj[i] = 1
            ##!! To maintain a self-avoiding walk, coordinates from the walk
            ##!! should be excluded from the neighborhood of the current pivot.
            #parray aCoordHash0
        scoordAdj = str(coordAdj)
        if not aCoordHash0.has_key(scoordAdj):
            neighbSize += 1
            rList = f(coordAdj, aV['coordInitF'])
            valueAdj = rList
            aV['cntProbe'] += 1
            #!! aggregate coordBestList for random selection later
            if valueAdj <= valueBest:
                if valueAdj < valueBest:
                    coordBestList = []
                    valueBest = valueAdj
                    coordBest = list(coordAdj)
                    coordBestList.append(coordBest)
                if aV['writeVar'] == 3:
                    distance = B.coord.distance(coordAdj, coordPiv)
                    rank = B.coord.rank(coordAdj)
                    rowLines += str(aV['cntProbe']) + "\t" + str(i) + "\t" + str(coordBest) + "\t" + str(valueBest) + "\t" + str(coordAdj) + "\t" + str(rList) + "\t" + str(distance) + "\t" + str(rank) + "\n"
    #if aV['writeVar'] == 3:
        #print(rowLines)
        #!! randomize the choice of coordBest from coordBestList
    idx = int(random.random()*len(coordBestList))
    if len(coordBestList) > 0:
        coordBest = coordBestList[idx]
    else:
        coordBest = None

    return str(coordBest) + " " + str(valueBest) + " " + str(neighbSize) + " " + str(coordProbedList) + " " + str(valueProbedList)

def patterns(instanceInit = [0, 0, 0, 0]):
    if isinstance(instanceInit, int):
        instanceInit = [int(i) for i in str(instanceInit)]
    L = len(instanceInit)
    M = 0
    N = 0
    if L == 4:
        N = 2
        M = 2
    if L == 6:
        M = 2
        N = 3
    if L == 9:
        M = 3
        N = 3
    if L == 16:
        M = 4
        N = 4
    mP = [[[0 for k in xrange(-1, L)] for j in xrange(N)] for i in xrange(M)]
    for i in range(M):
        for j in range(N):
            k = (i)*N + j
            mP[i][j][-1] = int(instanceInit[k])
    if L == 4:
        for k in xrange(L):
            if k == 0:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[1][0][k] = 1
            elif k == 1:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[1][1][k] = 1
            elif k == 2:
                mP[0][0][k] = 1
                mP[1][0][k] = 1
                mP[1][1][k] = 1
            elif k == 3:
                mP[0][1][k] = 1
                mP[1][0][k] = 1
                mP[1][1][k] = 1
            for i in range(M):
                rows = []
                for j in range(N):
                    rows.append(mP[i][j][k])
                    #print(rows)

    if L == 6:
        for k in xrange(L):
            if k == 0:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[1][0][k] = 1
            elif k == 1:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[0][2][k] = 1
                mP[1][1][k] = 1
            elif k == 2:
                mP[0][1][k] = 1
                mP[0][2][k] = 1
                mP[1][2][k] = 1
            elif k == 3:
                mP[0][0][k] = 1
                mP[1][0][k] = 1
                mP[1][1][k] = 1
            elif k == 4:
                mP[0][1][k] = 1
                mP[1][0][k] = 1
                mP[1][1][k] = 1
                mP[1][2][k] = 1
            elif k == 5:
                mP[0][2][k] = 1
                mP[1][1][k] = 1
                mP[1][2][k] = 1
            for i in range(M):
                rows = []
                for j in range(N):
                    rows.append(mP[i][j][k])
                    #print(rows)

                
    if L == 9:
        for k in xrange(L):
            if k == 0:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[1][0][k] = 1
            elif k == 1:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[0][2][k] = 1
                mP[1][1][k] = 1
            elif k == 2:
                mP[0][1][k] = 1
                mP[0][2][k] = 1
                mP[1][2][k] = 1
            elif k == 3:
                mP[0][0][k] = 1
                mP[1][0][k] = 1
                mP[1][1][k] = 1
                mP[2][0][k] = 1
            elif k == 4:
                mP[0][1][k] = 1
                mP[1][0][k] = 1
                mP[1][1][k] = 1
                mP[1][2][k] = 1
                mP[2][1][k] = 1
            elif k == 5:
                mP[0][2][k] = 1
                mP[1][1][k] = 1
                mP[1][2][k] = 1
                mP[2][2][k] = 1
            elif k == 6:
                mP[1][0][k] = 1
                mP[2][0][k] = 1
                mP[2][1][k] = 1
            elif k == 7:
                mP[1][1][k] = 1
                mP[2][0][k] = 1
                mP[2][1][k] = 1
                mP[2][2][k] = 1
            elif k == 8:
                mP[1][2][k] = 1
                mP[2][1][k] = 1
                mP[2][2][k] = 1

            for i in range(M):
                rows = []
                for j in range(N):
                    rows.append(mP[i][j][k])
                    #print(rows)
    if L == 16:
        for k in xrange(L):
            if k == 0:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[1][0][k] = 1
            elif k == 1:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[0][2][k] = 1
                mP[1][1][k] = 1
            elif k == 2:
                mP[0][1][k] = 1
                mP[0][2][k] = 1
                mP[0][3][k] = 1
                mP[1][2][k] = 1
            elif k == 3:
                mP[0][2][k] = 1
                mP[0][3][k] = 1
                mP[1][3][k] = 1
            ####
            elif k == 4:
                mP[0][0][k] = 1
                mP[1][0][k] = 1
                mP[1][1][k] = 1
                mP[2][0][k] = 1
            elif k == 5:
                mP[0][1][k] = 1
                mP[1][0][k] = 1
                mP[1][1][k] = 1
                mP[1][2][k] = 1
                mP[2][1][k] = 1
            elif k == 6:
                mP[0][2][k] = 1
                mP[1][1][k] = 1
                mP[1][2][k] = 1
                mP[1][3][k] = 1
                mP[2][2][k] = 1
            elif k == 7:
                mP[0][3][k] = 1
                mP[1][2][k] = 1
                mP[1][3][k] = 1
                mP[2][3][k] = 1
            ####
            elif k == 8:
                mP[1][0][k] = 1
                mP[2][0][k] = 1
                mP[2][1][k] = 1
                mP[3][0][k] = 1
            elif k == 9:
                mP[1][1][k] = 1
                mP[2][0][k] = 1
                mP[2][1][k] = 1
                mP[2][2][k] = 1
                mP[3][1][k] = 1
            elif k == 10:
                mP[1][2][k] = 1
                mP[2][1][k] = 1
                mP[2][2][k] = 1
                mP[2][3][k] = 1
                mP[3][2][k] = 1
            elif k == 11:
                mP[1][3][k] = 1
                mP[2][2][k] = 1
                mP[2][3][k] = 1
                mP[3][3][k] = 1
            ####
            elif k == 12:
                mP[2][0][k] = 1
                mP[3][0][k] = 1
                mP[3][1][k] = 1
            elif k == 13:
                mP[2][1][k] = 1
                mP[3][0][k] = 1
                mP[3][1][k] = 1
                mP[3][2][k] = 1
            elif k == 14:
                mP[2][2][k] = 1
                mP[3][1][k] = 1
                mP[3][2][k] = 1
                mP[3][3][k] = 1
            elif k == 15:
                mP[2][3][k] = 1
                mP[3][2][k] = 1
                mP[3][3][k] = 1
    
            for i in range(M):
                rows = []
                for j in range(N):
                    rows.append(mP[i][j][k])
        #print(rows)

    retVal = [M, N, mP]
    #print(retVal)
    return retVal

def f(coord = [1, 0, 1, 0, 1, 0]):
    fVal = 0
    isTestOnly = 0
    if aV['valueTarget'] == -1:
        return fVal
    #if isTestOnly:
    #instanceDef = [3, 3]
    M = aV['M']
    N = aV['N']
    L = aV['nDim']

    # initialize matrix mInit and mAdd
    mInit = [x[:] for x in [[0]*N]*M]
    mAdd = [x[:] for x in [[0]*N]*M]

    for i in xrange(M):
        for j in xrange(N):
            mInit[i][j] = aStruc[i][j][-1]
            mAdd[i][j] = 0
            # optionally, print the initial matrix
            
    if isTestOnly:
        print("================")
        print("\n.. the initial mark, constructed from instanceInit = " + str(aV['instanceInit']))
        for i in range(1, M):
            row = []
            for j in range(1, N):
                row.append(mAdd[i][j])
                #print(row)

    # compute the mod-2 sum of all asserted matrix patterns
    for k in range(L):
        isAsserted = coord[k]
        
        if isAsserted:
            for i in range(M):
                for j in range(N):
                    mAdd[i][j] = (mAdd[i][j] + aStruc[i][j][k]) % 2
                    #print("k=" + str(k))
            for i in range(M):
                row = []
                for j in range(N):
                    row.append(mAdd[i][j])
                    #print(row)
                    # optionally, print the mod-2 addition matrix
    if isTestOnly:
        for i in range(1, M):
            row = []
            for j in range(1, N):
                mAdd[i][j]
                print(row)
                print("================")

    fVal = 0
    for i in range(M):
        for j in range(N):
            val = (mInit[i][j] + mAdd[i][j]) % 2
            fVal += val
            #print("coord_value_pair = " + str(coord) + ":" + str(fVal))
    return fVal

def exhA(instanceInit = [1, 1, 0, 1, 0, 0]):
    thisCmd = "B_lightp.exhA"
    
    L = len(instanceInit)
    rList = patterns(instanceInit)
    M = rList[0]
    N = rList[1]
    aStruc = rList[2]
    #print("gv = " + str(aStruc))

    if len(rList) == 4 and rList[3] == 0:
        aV['valueTarget'] = -1
    else:
        aV['valueTarget'] = None

    aV['M'] = M
    aV['N'] = N
    aV['L'] = L

    ##!< initialize aV also to support testing of 
    ##!< B.lightp.f, B.lightp.saw.pivot.simple, and B.lightp.saw.pivot 
    aV['writeVar'] = 3
    aV['instanceInit'] = instanceInit
    aV['varList'] = []
    for i in range(1, L):
        aV['varList'].append(i)
        #print(aV)
        #return

    coordList = []
    
    # generate an exhaustive list of coordinates (use *.exhB when L > 9)
    for i in range(int(pow(2, L))):
        # print("i: " + str(i) + "nDim: " + str(nDim))
        #   tmp = B_coord.coord_from_int(i, nDim)
        #  if not tmp in coordList:
        coordList.append(B.coord.from_int(i, L))
        #print("coordList\n" + str(coordList) + "\n")
        # perform exhaustive enumeration
    valueMin = 1e30

    bestCoord = []
    bestRank = 0
    
    for coord in coordList:
        #print("Coord: " + str(coord))########################
        value = f(coord)
        #print("value = " + str(value)) 
        rank = B.coord.rank(coord)
        if not hasseAry.has_key(rank):
            hasseAry[rank] = []
            hasseAry[rank].append(str(coord) + ":" + str(int(value)))

        #hasseAry.get(rank, default = []).append(coord)
        #hasseAry[rank].append(coord)
        if value < valueMin:
            valueMin = value
    if L <= 6:
        print("\n")
        pprint(hasseAry)
        print("\n")
        
    rankMax = len(hasseAry) - 1
    bestAry = {}
    
    print("coordRank\tcoordTotal")
    widthMax = 0

    for rank in hasseAry:
        width = len(hasseAry[rank])
        if width > widthMax:
            widthMax = width
            listBest = [x for x in hasseAry[rank] if int(x.split(':')[1]) == valueMin]
        if len(listBest) != 0:
            bestAry[rank] = listBest
            #print(str(rank) + "\t" + str(width) + "\t" + str(hasseAry))
        print(str(rank) + "\t" + str(width))

    print("\nvalueBest = " + str(valueMin))

    for rank in hasseAry:
        if bestAry.has_key(rank):
            print("solutionBest(rank=" + str(rank) + ") = " + str(bestAry[rank]))
            #print(str(rank) + "\t" + str(width) + "\t" + str(hasseAry[rank]))
    
    print("instanceInit = " + str(instanceInit))
    # this feature is needed for the follow-up tcl proc $B.lightp.hasse
    if aV['L']  <= 6:
        print("\n.. values returned by " + thisCmd + " for  processing by B.lightp.hasse")
        return ["B", aV['L'], rankMax, widthMax, coordList, bestAry, hasseAry]
    else:
        return

def exhB(instanceInit = [1, 1, 0, 1, 0, 0]):
    global aStruc
    global aV
    global aCoordHash
    global hasse
    thisCmd =  "B.lightp.exhB"
    sandbox = "B.lightp"
    ABOUT = """
Example:        B.lightp.exhB [1, 1, 0, 1, 0, 0] (under python)
        ../xBin/B.lightp.exhB [1, 1, 0, 1, 0, 0] (under bash)

This command B.lightp.exhB takes a binary coordinate instanceInit of length L that defines the
initial configuration of lights-out in the puzzle under the sandbox B.lightp.
The procedure iteratively generates 2^L binary coordinates to perform an
exhaustive evaluation of the 'lightout puzzle puzzle' instance which is
specified by the value of instanceInit. The principle behind this coordinate
generation is repeated re-use of the associative array aCoordHash0. Given
this array, the generation proceeds from all coordinates at rank k to all
coordinates at rank k+1. The value of k is in the range \[0, L\]. The
exhaustive evaluation includes comprehensive instrumentation to measure the
computational cost and the efficiency of the procedure.
        
For a stdout query, use one of these these commands:
        B.lightp.exhB  ??  (after running the file all_tcl under python)
    ../xBin/B.light.exhBB  (immediately executable under bash)
"""
   
    if instanceInit == "??":
        print ABOUT
        return
    if instanceInit == "?":
        print ("Valid query is '{} ??'").format(thisCmd)
        return
    
    #-- initialize all matrix patterns
    L = len(instanceInit)
    rList = patterns(instanceInit)
    M = rList[0]
    N = rList[1]
    aStruc = rList[2]

    aV = { "M" : M, "N" : N, "nDim" : L, "valueTarget" : 0}
    # since we are dealing with binary coordinates
    rankMax = L
    
    # define coordinate:value pair with rank=0
    coordRef = [0 for x in range(L)]
    coordList0 = [list(coordRef)]
    value = B.lightp.f(coordRef)
    valueBest = 1e30
    bestAry = {value: ["000_"+",".join(imap(str,coordRef))+":"+str(value)]}
    coordDistrib = {"000":1}
    sizeTot = 1

    # For each rank, unset aCoordHash0 before aggregating coordList1
    # then probe B.lightp.f for function value
    aCoordHash = {}
    coordList1 = []
    runtimeCoord = 0.0
    runtimeProbe = 0.0
    if L <= 5:
        hasseVertices = {(0,1): [",".join(imap(str,coordRef)) + ":" + str(value)] }

    sizeRank = 0

    # at each rank, generate all unique coordinates and probe for function values
    for rank in xrange(1, rankMax+1):

        #!! #** timing starts for coordList ***
        # given coordList0, compute coordList1, up to rankMax
        microSecs = time.time()
        #pprint(coordList0)
        for coord in coordList0:
            for k in xrange(L):
                bit = coord[k]
                coordAdj = list(coord)
                if bit:
                    coordAdj[k] = 0
                else:
                    coordAdj[k] = 1
                weight = B.coord.rank(coordAdj)
                if weight == rank and not (",".join(imap(str,coordAdj)) in aCoordHash):
                    aCoordHash[",".join(imap(str,coordAdj))] = []
                    coordList1.append(coordAdj)
                    sizeTot += 1
                    sizeRank += 1
        #end timing
        microSecs = time.time() - microSecs
        # RECORD runtimeCoord for current rank
        runtimeCoord += microSecs

        # now, probe each coordinate at current rank for function value
        #!! #** timing starts ***
        microSecs = time.time()
        for coord in coordList1:
            value = f(coord)
            solutionString = ",".join(imap(str,coord))+":"+str(value)
            if L <= 5:
                if (rank,sizeRank) in hasseVertices:
                    hasseVertices[(rank,sizeRank)].append(solutionString)
                else:
                    hasseVertices[(rank,sizeRank)] = [solutionString]
            if value < valueBest:
                coordString = "{:03}_".format(rank)+solutionString
                if bestAry.has_key(value):
                    bestAry[value].append(coordString)
                else:
                    bestAry[value] = [coordString]
        # end timing
        microSecs = time.time() - microSecs
        runtimeProbe += microSecs

        # reinitialize parameters to generate coordinates at the next rank
        coordDistrib["{:03}".format(rank)] = sizeRank
        coordList0 = coordList1[:]
        aCoordHash = {}
        coordList1 = []
        sizeRank = 0


    # find valueBest solutions
    valueMin = min(bestAry)
    print "\nThere are {} valueBest = {} solutions for instanceInit={}:\nrank\tsolution".format(len(bestAry[valueMin]), valueMin, instanceInit)

    for item in bestAry[valueMin]:
        item = item.split("_")
        rank = item[0]
        solution = item[1]
        print rank+"\t"+solution

    # Output file stuff
    print "\n".join([
        "\n",
        "instanceInit = {}, M = {} (rows), N = {} (columns)".format(instanceInit, M, N),
        "There are {} valueBest = {} solutions".format(len(bestAry[valueMin]),
            valueMin),
        "rankMax = {}".format(rankMax),
        "coordLength = {}".format(L),
        "coordTotal = {}".format(sizeTot),
        "runtimeCoord = {:6.5}".format(runtimeCoord),
        "runtimeProbe = {:6.5}".format(runtimeProbe),
        "runtimeRatio = {:6.5}".format(runtimeCoord/runtimeProbe),
        "hostID = {}@{}-{}-{}".format(pwd.getpwuid(os.getuid())[0],
            os.uname()[1], platform.system(), os.uname()[2]),
        "compiler = python-"+".".join(imap(str,sys.version_info[:3])),
        "dateLine = {}".format(time.strftime("%a %b %d %H:%M:%S %Z %Y")),
        "thisCmd = {}\n".format(thisCmd)])
    
    for key in sorted(coordDistrib):
        print "coordDistrib({})".format(key)+" =",coordDistrib[key]

    """

    coordAry = {}
    coordAry[0] = []
    for i in range(nDim):
        coordAry[i] = []
        coordAry[0].append([0 for x in range(nDim)])
        #print(str(coordAry))

    cntCoord = 1
    coordDistrib = {0:1}
    valueBest = 1e30
    
    runtimeCoord = 0.0
    runtimeProbe = 0.0

    for rank in range(1, nDim + 1):
        coordDistrib[rank] = 0
        aCoordHash = {}

        microSecs = time.time()
        #print(str(microSecs))
        for coord in coordAry[rank - 1]:
            for i in range(nDim):
                cAdj = list(coord)
                if cAdj[i]:
                    cAdj[i] = 0
                else:
                    cAdj[i] = 1
                    #print(str(cAdj))
                weight = B.coord.rank(cAdj)
                scAdj = str(cAdj)
                if weight == rank and not aCoordHash.has_key(scAdj):
                    aCoordHash[scAdj] = []
                    if not coordAry.has_key(weight):
                        coordAry[weight] = []
                        coordAry[weight].append(cAdj)
                        cntCoord += 1
                        coordDistrib[rank] += 1
                        #pprint(coordDistrib)
                        #print(cAdj)
        microSecs = time.time() - microSecs
        #print(str(microSecs))
        runtimeCoord += microSecs
        #print(str(coordAry))
    if nDim <= 6:
        pprint(coordAry)

    print("\
      \n instanceDef = {}\
      \n coordLength = {}\
      \n coordTotal  = {}\
      \n runtimeCoord = {:6.4}\
      \n hostID = {}@{}-{}-{}\
      \n dateLine = {}\
      \n thisCmd = {}\n".format(instanceDef, nDim, cntCoord, runtimeCoord, getpass.getuser(), os.uname()[1], platform.system(), os.uname()[2], time.strftime("%a %b %H:%M:%S %Z %Y"), "exhB()"))
    
    pprint(coordDistrib)
    """
    return

#Code attained from: http://stackoverflow.com/questions/13214809/pretty-print-2d-python-list
#Used for testing reasons
def prettyPrint(matrix):
    s = [[str(e) for e in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print '\n'.join(table)

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def stdout( withWarning = 1 ):
    ABOUT = ("This procedure outputs results afer a successful completion of "
             "a combinatorial solver. The output is directed to 'stdout' and "
             "includes a solution (a coordinate-value pair) and the observed "
             "performance values. The format consists of a few comment lines, "
             "followed by a tabbed name-value pairs. The first piar is always\n"
             "instanceDef <value>\n"
             "This procedure is universal under any function coordType=P!")
    thisCmd = "B.lightp.stdout"
    
    #info global vairables
    global all_info
    global all_value
    global aV

    print ("# \n# FROM {}: A SUMMARY OF NAME-VALUE PAIRS"
           "\n# commandLine = {}"
           "\n#    dateLine = {}"
           "\n#   timeStamp = {}"
           "\n#".format(thisCmd, aV["commandLine"], aV["dateLine"], aV["timeStamp"]))

    stdoutNames = ("instanceDef", "solverID", "coordInit", "coordBest", "nDim",
                   "walkLengthLmt", "walkLength", "cntRestartLmt", "cntRestart", 
                   "cntProbeLmt", "cntProbe", "runtimeLmt", "runtime", "runtimeRead", 
                   "speedProbe", "hostID", "isSimple", "neighbDist", "solverMethod",
                   "walkSegmLmt", "walkSegmCoef", "walkIntervalLmt", "walkIntervalCoef",
                   "walkRepeatsLmt", "seedInit", "valueInit", "valueBest", "valueTarget",
                   "valueTol", "targetReached", "isCensored")

    for name in stdoutNames:
        if name in aV:
            print "{}\t\t{}".format(name, aV[name])
        else:
            if withWarning:
                print "# WARNING: no value exist for {}".format(name)

def saw(arg=""):
    thisCmd = "B.lightp.saw"
    ABOUT = """
        Procedure $thisCmd takes global array values initialized under B.lightp.init
        and constructs a segment of a self-avoiding walk (SAW). Either B.lightp.saw.pivot.simple
        or the significantly more efficient procedure B.lightp.saw.pivot.ant is invoked.
        More to come ....
        """
    if arg == "??":
        print ABOUT
        return
    elif arg == "?":
        print "Valid query is '{} ??'".format(thisCmd)
        return
    #raise Exception("Valid query is '{} ??'".format(thisCmd))
    #sys.stderr.write("Valid query is '{}' ??'\n".format(thisCmd))
    #sys.exit(1)
    
    # info global variables
    global all_info
    global all_valu
    global aV
    # instance global variables
    global aStruc
    # solver global variables
    global aCoordHash0
    global aWalkProbed

    # primary input variables
    functionID = aV["functionID"]
    runtimeLmt = aV["runtimeLmt"]
    cntProbeLmt = aV["cntProbeLmt"]
    #walkRepeatsLmt = aV["walkRepeatsLmt"]
    #walkIntervalLmt = aV["walkIntervalLmt"]
    walkSegmLmt = aV["walkSegmLmt"]
    valueTarget = aV["valueTarget"]
    
    if aV["isSimple"]:
        procPivotNext = saw_pivot_simple
    else:
        procPivotNext = saw_pivot
    print "# FROM: {}, searching for pivotBest via {}".format(thisCmd,
                                                          procPivotNext.__name__)
    # auxiliary variables
    aV["coordPivot"] = aV["coordInit"]
    aV["valuePivot"] = aV["valueInit"]
    aV["coordBest"] = aV["coordPivot"]
    aV["valueBest"] = aV["valuePivot"]
    step = 0
    
    while True:
        # Timing
        microSecs = time.time()
        
        # UPDATE walkLength
        step += 1
        aV["walkLength"] += 1
        # PROBE neighborhood of current pivot
        bestNeighb = procPivotNext(aV["coordPivot"], aV["valuePivot"])
        
        # SELECT next pivot
        aV["coordPivot"] = bestNeighb[0]
        aV["valuePivot"] = bestNeighb[1]
        aV["neighbSize"] = bestNeighb[2]
        print("NEIGHBSIZE:" + str(aV["neighbSize"]))
        if aV["isWalkTables"]:
            aV["coordProbedList"] = bestNeighb[3]
            aV["valueProbedList"] = bestNeighb[4]
            
            walkLengthM1 = aV["walkLength"] - 1
            neighbSize = 0
            isPivot = 0
            for coord, value in aV["coordProbedList"], aV["valueProbedList"]:
                neighbSize += 1
                rank = P.coord.rank(coord)
                aWalkProbed[(walkLengthM1,neighbSize)] = ( walkLengthM1,
                                                          aV["cntRestart"], coord, value, rank, isPivot,
                                                          neighbSize, None)
            isPivot = 1
            aV["rankPivot"] = P.coord.rank(aV["coordPivot"])
            aWalkProbed[(aV["walkLength"],0)] = (aV["walkLength"],
                                                 aV["cntRestart"], aV["coordPivot"], aV["valuePivot"],
                                                 aV["rankPivot"], isPivot, aV["neighbSize"], aV["cntProbe"])
        
        if aV["coordPivot"] is not None:
            aCoordHash0[tuple(aV["coordPivot"])] = []
        
        # UPDATE valueBest, aValueBest, aWalkBest
        if aV["valuePivot"] <= aV["valueBest"]:
            aV["valueBest"] = aV["valuePivot"]
            aV["coordBest"] = aV["coordPivot"]
        # CHECK the nighboroodSize
        if aV["neighbSize"] == 0:
            aV["isBlocked"] = 1
            aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
            print ("WARNING from {}: isBlocked=1, aV['neighbSize']={} ..."
                   "no available neighborhood coordinates ...".format(thisCmd,
                                                                      aV["neighbSize"]))
            return
        #end timing
        microSecs = time.time() - microSecs
        
        # Record runtime for step
        aV["runtime"] += microSecs
        aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
        
        if aV["valueBest"] <= valueTarget:
            break
    
        if aV["cntProbe"] > cntProbeLmt:
            aV["isCensored"] = 1
            aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
            print ("WARNING from {}: isCensored=1, cntProbe={} > cntProbeLmt"
                   "={}\n".format(thisCmd, aV["cntProbe"], aV["cntProbeLmt"]))
            return
        if aV["runtime"] > runtimeLmt:
            aV["isCensored"] = 1
            aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
            print ("WARNING from {}: isCensored=1, runtime={} > runtimeLmt"
                   "={}\n".format(thisCmd, aV["runtime"], aV["runtimeLmt"]))
            return

    if aV["valueBest"] == aV["valueTarget"]:
        aV["targetReached"] = 1
    elif aV["valueBest"] < aV["valueTarget"]:
        aV["targetReached"] = 2
    else:
        aV["targetReached"] = 0
    
    return aV["targetReached"]

def saw_pivot(coordPiv=[5,3,2,1,4], valuePiv=-46):
    thisCmd = "B.lightp.saw.pivot"
    ABOUT = """
        This procedure takes a pivot coordinate/value, probes the distance=1
        neighborhood of a 'lightp' (a linear ordering probelm), subject to the
        constraints of a SAW (self-avoiding walk) -- i.e. the best coord/value it
        returns has not been yet been selected as the pivot for the next step.
        Neighborhood size of 0 signifies that the next step of a SAW is blocked.
        \n This implementation is 'FAST', i.e. for each pivot coordinate of length L,
        there are up to L-1 FAST tableau-based probes of each pivot coordinate.
        """
    if coordPiv == "??":
        print ABOUT
        return
    elif coordPiv == "?":
        print "Valid query is '{} ??'".format(thisCmd)
        return
    #raise Exception("Valid query is '{} ??'".format(thisCmd))
    #sys.stderr.write("Valid query is '{}' ??'\n".format(thisCmd))
    #sys.exit(1)

    # info global variables
    global all_info
    global all_valu
    global aV
    # instance global variables
    global aStruc
    # Solver global variables
    global aCoordHash0
    global aWalkProbed

    coordBest = None
    valueBest = 2147483641 #@TODO: change to max int
    valueProbedList = []
    coordBestList = []
    neighbSize = 0
    coordProbedList = []

    M = aV["M"]
    N = aV["N"]
    L = aV["nDim"]

    rList = fAdj(coordPiv)
    valuePiv = rList[0]
    aValueAdj = rList[1]

    valueOrderedList = list(aValueAdj)
    valueOrderedList.sort()

    if aV["writeVar"] == 3:
        pprint(aValueAdj)
        pprint(aCoordHash0)

    isBestFound = False
    neighbSize = aV["neighbSize"]
    for value in valueOrderedList:
        for coord in aValueAdj:
            if len(coord) and not aCoordHash0.has_key(str(coord)):
                coordBest = coord
                valueBest = value
                isBestFound = True
            if isBestFound:
                break;
            else:
                neighbSize -= 1
        if isBestFound:
            break;
    return [coordBest, valueBest, neighbSize]

def fAdj(coordPiv = [1,0,1,0,1,0]):
    thisCmd = "B.lightp.fAdj"
    ABOUT = """
        Procedure $thisCmd takes global array values initialized under B.lightp.init
        and constructs a segment of a self-avoiding walk (SAW). Either B.lightp.saw.pivot.simple
        or the significantly more efficient procedure B.lightp.saw.pivot.ant is invoked.
        More to come ....
        """
    if coordPiv == "??":
        print ABOUT
        return
    elif coordPiv == "?":
        print "Valid query is '{} ??'".format(thisCmd)
        return
    # info global variables
    global all_info
    global all_valu
    global aV
    # instance global variables
    global aStruc

    M = aV["M"]
    N = aV["N"]
    L = aV["nDim"]

    mInit = [x[:] for x in [[0]*N]*M]
    mAdd = [x[:] for x in [[0]*N]*M]
    for i in range(M):
        for j in range(N):
            mInit[i][j] = aStruc[i][j][-1]
            mAdd[i][j] = 0

    for k in range(L):
        isAsserted = int(coordPiv[k])
        if isAsserted:
            for i in range(M):
                for j in range(N):
                    mAdd[i][j] = (mAdd[i][j] + aStruc[i][j][k]) % 2
                for i in range(M):
                    row = []
                    for j in range(N):
                        row.append(mAdd[i][j])

    valuePiv = 0
    mTot = [x[:] for x in [[0]*N]*M]
    mAdj = [x[:] for x in [[0]*N]*M]

    for i in range(M):
        for j in range(N):
            mTot[i][j] = (mInit[i][j] + mAdd[i][j]) % 2
            valuePiv = valuePiv + mTot[i][j]
    aV["cntProbe"] += 1

    aCoordAdj = {}
    #aValueAdj = [x for x in [[]]*L]
    aValueAdj = {}

    for k in range(L):
        bit = coordPiv[k]
        coordAdj = list(coordPiv)
        if bit:
            coordAdj[k] = 0
        else:
            coordAdj[k] = 1
        valueAdj = 0
        for i in range(M):
            for j in range(N):
                mAdj[i][j] = (mTot[i][j] + aStruc[i][j][k]) % 2
                valueAdj = valueAdj + mAdj[i][j]
        aCoordAdj[str(coordAdj)] = valueAdj
        aValueAdj[str(valueAdj)].append(coordAdj)

    aV["cntProbe"] += 1
    if aV["writeVar"] == 3:
        print("fjskldfjdskflsjdfklsadjfskl TODO: Finish this")
    return [valuePiv, aValueAdj]
    
#if __name__ == "__main__":
#main("i-16-a-0")
#main("?")
#main("i-16-a-0", true, 1901, true)
#print("patterns()")
#prettyPrint(patterns())
#print("f()")
#print(f([0, 0, 0, 1, 0, 1, 1, 0, 1], [1, 0, 1, 0, 0, 0, 0, 0, 0]))
#print(f([1, 1, 1, 0, 0, 0, 1, 1, 0], [0, 1, 0, 0, 0, 1, 0, 0, 1]))
#print("exhA()")
#exhA([2, 2], 1215)
#exhA([3, 3])
#exhA([3, 3], 3872)
#exhA([3, 3], 5914)
#exhA([3, 3], -1)
#exhA([2, 2], 1215)
#print(exhA([0, 1, 1, 0]))
#print(exhA([1, 0, 0, 0, 0, 0]))
#print("exhB()")
#exhB()
#print("saw_pivot_simple()")
#print(saw_pivot_simple([1, 1, 0, 0], 3))
#print(saw_pivot_simple([0, 1, 1, 1], 3))
#print(saw_pivot_simple([0, 0, 0, 0, 0, 1], 6))
