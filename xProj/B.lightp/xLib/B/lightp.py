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

import math

def main( instanceDef, args = [] ):
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
    
    #!! (1) Phase 1: query about commandLine **OR**
    #           initialize all variables
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
            "\n.. completed initialization of all variables under {},"
            "\n   exiting the solver since option -{} has been asserted."
            "\n{}\n".format("-"*78,aV["isInitOnly"],thisCmd,"-"*78))
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
        print("# {}"
            "\n# .. completed initialization of all variables under {},"
            "\n# .. proceeding with the search under solverID = B.lightp.{}"
            "\n# {}").format("-"*78,thisCmd,aV["solverMethod"],"-"*78)

    # (2) Phase 2: proceed with the combinatorial search
    if aV["solverMethod"] == "saw":
        aV["solverID"] = saw
    else:
        print "\nERROR from {}:\nsolverMethod = {} is not implemented\n".format(thisCmd, aV["solverMethod"])
        return
    #print "#    Proceeding with the search under solverID = B.lightp.{}".format(aV["solverID"].__name__)
    #print "#"*78
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

    print "\n".join([
        "USAGE:",
        "under TkCon shell (which has sourced ../xLib/all_tcl):",
        "B.lightp.main instanceDef [optional_arguments]",
        "",
        "under bash, invoking the 'tcl executable B.lightpT' which sources libraries directly",
        "../xBin/B.lightpT instanceDef [optional_arguments]",
        "",
        "under bash, invoking the 'python executable B.lightpP' which sources libraries directly",
        "../xBin/B.lightpP instanceDef [optional_arguments]",
        "",
        "under bash, invoking the 'compiled C++ code as as a binary B.lightpX'",
        "../xBin/B.lightpX  instanceDef [optional_arguments]",
        "",
        "EXAMPLES:",
        "B.lightp.main     i-9-a-0  -isInitOnly",
        "B.lightp.main     i-9-a-0  -seedInit 1215",
        "../xBin/B.lightpT i-9-a-0  -seedInit 1215  -coordInit 101100101 -isSimple",
        "../xBin/B.lightpP i-9-a-0  -seedInit 1215  -coordInit 101100101",
        "../xBin/B.lightpT i-25-a-0 -seedInit 1215  -runtimeLmt 5 -isSimple",
        "../xBin/B.lightpT i-25-a-0 -seedInit 1215  -runtimeLmt 5",
        "",
        "DESCRIPTION:",
        "B.lightp.main, B.lightpT, B.lightpP, or B.lightpX take one REQUIRED argument"
        "",
        "instanceDef  (an instance name recognized under B.lightp/xBenchm)"
        "",
        "and a number of OPTIONAL arguments in any order."
        "",
        "Here is a complete list of 'name defaultValue' options, with short",
        "in-line descriptions for each option:"
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
        "This solver reads from an instance name of the 'lights-out puzzle",
        "problem' associated with a binary string which can be of length 4=2*2,",
        "6=2*3, 9=3*3, 12=3*4, 16=4*4, 20=4*5, 25=5*5, 30=5*6, 36=6*6, 42=6*7, etc.",
        "This string represents lights that are 'on' in a rectangular matrix of",
        "size L=M*N. The solver returns a solution as a coordinate:value pair:",
        "the coordinate is a binary string of length L, and the minimum",
        "value is 0 for most instances; for some instances, the minimum",
        "value is 1.",
        "",
        "For the instance shown below, there exist a single solution only!",
        "",
        "instanceInit     solutionBest",
        " 001001011         001101001",
        "lights-on= 4     lights-on= 0",
        "------------     ------------",
        "  0 0 1            0 0 0",
        "  0 0 1            0 0 0",
        "  0 1 1            0 0 0",
    ])

    return

def init( instanceDef, args = [] ):
    thisCmd = "B.lightp.init"
    mainProc = "B.lightp.main"
    ABOUT = """
        Procedure {} takes a variable number of arguments:
        'instanceDef' as the required argument and optional arguments in any order.
        It then  decodes values of optional arguments  and initializes all variables
        under global arrays. {} is invoked by {}; for details about
        the command-line structure, query '{} ??'.
        
        Procedure {} implicitly returns initialized global variables as well as
        explicit values of
        
        'targetReached  coordInit valueInit'.
        """.format(thisCmd, thisCmd, mainProc, mainProc, thisCmd)
    
    if instanceDef == "??":
        print ABOUT
        return
    if instanceDef == "?":
        print "Valid query is '{} ?? '".format(thisCmd)
        return

    # info global variables
    global all_info
    global all_valu
    global aV
    # instance global variables 
    global aStruc
    # solver global variables
    global aWalkProbed
    global aValueBest
    global aCoordHash0

    argsOptions = args

    rList = info(0, all_info["infoVariablesFile"])
    all_info = rList[0]
    all_valu = rList[1]

    # (0A) Phase 0A: initialize global variables
    aV = {}
    aStruc = {}
    aCoordHash0 = {}
    aWalkProbed = {}

    print "\n".join([
        "# FROM: {}:".format(thisCmd),
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
            firstChar = line[0]
            if firstChar != "#":
                rListTmp.append(line)
    isFound = False
    for line in rListTmp:
        line = line.split()
        varName = line[0]
        if varName == aV["instanceDef"]:
            aV["instanceInit"] = line[1]
            aV["valueTarget"] = line[2]
            aV["isProven"] = line[3]
            aV["nDim"] = len(aV["instanceInit"])
            aV["instanceDim"] = aV["nDim"]
            aV["coordRef"] = "0" * aV["nDim"]
            aV["varList"] = []
            for i in range(1, aV["nDim"] + 1):
                aV["varList"].append(i)
            #try:
            #   aV["isProven"] = int(line[2].strip('-'))
            #except:
            #   aV["isProven"] = False
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
                    if name == "coordInit":
                        aV[name] = tmpList[1]
                    else:
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
    if aV["coordInit"] == "NA":
        # generate a random permutation coordinate
        aV['coordInit'] = B.coord.rand(aV["nDim"])
        aV['rankInit'] = B.coord.rank(aV["coordInit"])
    else:
        # check if user provided coordInit is the valid length
        aV["coordInit"] = map(int, aV["coordInit"])
        #aV["coordInit"] = str(aV["coordInit"])
        if len(aV["coordInit"]) != aV["nDim"]:
            print ("\nERROR from {}:"
                "\nThe binary coordinate is of length {},"
                "not the expected length {}\n").format(thisCmd, len(aV["coordInit"]), aV["nDim"])
            return
        aV["rankInit"] = B.coord.rank(aV["coordInit"])

    if aV["walkSegmLmt"] == "NA" and aV["walkSegmCoef"] != "NA":
        try:
            walkSegmCoef = int(aV["walkSegmCoef"])
            if walkIntevalCoef > 0.:
                aV["walkSegmLmt"] = float(walkSegmCoef * aV["nDim"])
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
    aV["neighbSize"] = aV["nDim"]
    aV["coordPivot"] = aV["coordInit"]
    aV["valuePivot"] = aV["valueInit"]
    aV["coordBest"] = aV["coordInit"]
    aV["valueBest"] = aV["valueInit"]
    aCoordHash0[tuple(aV["coordInit"])] = []

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
    # aV["neighbSize"] = aV["nDim"] - 1

    # (6) Phase 6: initialize special arrays that can be selected w/ arguments
    #       from command line
    if aV["isWalkTables"]:
        aV["isSimple"] = 1
        isPivot = 1
        aV["rankPivot"] = B.coord.rank(aV["coordPivot"])
        #aValueBest[aV["valueInit"]] = [0,0,aV["coordInit"]]
        #aWalkBest[aV["valueInit"]] = [0,0,aV["coordInit"],0,0]
        #aWalk[aV["cntStep"]] = "{} {} {} {} {} {}".format(aV["cntStep"], aV["cntRestart"], aV["coordPivot"], aV["valuePivot"], aV["neighbSize"], aV["cntProbe"])
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

def saw( Query="" ):
    thisCmd = "B.lightp.saw"
    sandbox = "B.lightp"
    initProc = "B.lightp.init"
    pivotProcSimple = "B.lightp.saw_pivot_simple"
    pivotProc = "B.lightp.saw_pivot"
    
    ABOUT = """
        Procedure {} takes, as global dictionaries, data structures
        initialized by {} under the sandbox $sandbox. It then constructs
        a segment of a self-avoiding walk (SAW). Under the command-line option
        -isSimple, the walk proceeds under the control of {},
        while by default the walk is controlled by a significantly more efficient
        procedure {}. Under various termination conditions, the walk
        stops and updates the global dictionaries; it also explicitly
        returns tuple of values, including the 0|1|2 status of targetReached:
        (targetReached coordBest valueBest)
        """.format(thisCmd, initProc, pivotProcSimple, pivotProc)
    if Query == "??":
        print ABOUT
        return
    elif Query == "?":
        print "Valid query is '{} ??'".format(thisCmd)
        return
    
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
    walkLengthLmt = aV["walkLengthLmt"]
    walkSegmLmt = aV["walkSegmLmt"]
    valueTarget = aV["valueTarget"]
    
    if aV["isSimple"]:
        procPivotNext = saw_pivot_simple
    else:
        procPivotNext = saw_pivot
    print "# FROM: {}, searching for pivotBest via B.lightp.{}**".format(thisCmd,
            procPivotNext.__name__)
    # auxiliary variables
    aV["coordBest"] = aV["coordInit"][:]
    aV["valueBest"] = aV["valueInit"]
    coord = aV["coordInit"][:]
    value = aV["valueInit"]
    
    step = 0
    
    while True:
        # Timing
        microSecs = time.time()
        
        # PROBE neighborhood of current pivot
        bestNeighb = procPivotNext(coord, value)
        # SELECT next pivot
        coordNext = bestNeighb[0]
        valueNext = bestNeighb[1]
        neighbSize = bestNeighb[2]
        
        aCoordHash0[tuple(coordNext)] = []
        #end timing
        microSecs = time.time() - microSecs
        
        # Record runtime for step
        aV["runtime"] += microSecs
        aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
        
        # UPDATE valueBest, aValueBest
        if valueNext <= aV["valueBest"]:
            aV["valueBest"] = valueNext
            aV["coordBest"] = coordNext
        if aV["isWalkTables"]:
            aV["coordProbedList"] = bestNeighb[3]
            aV["valueProbedList"] = bestNeighb[4]
            cntNeighb = 0
            isPivot = 0
            for coordPr, valuePr in aV["coordProbedList"], aV["valueProbedList"]:
                cntNeighb += 1
                rankPr = P.coord.rank(coord)
                aWalkProbed[(step,cntNeighb)] = (step, aV["cntRestart"],
                        coordPr, valuePr, rankPr, isPivot, cntNeighb, None)
            isPivot = 1
            neighbSize = cntNeighb
            rank = P.coord.rank(coord)
            aWalkProbed[(step,0)] = (step, aV["cntRestart"], coord, value,
                                     rank, isPivot, cntNeighb, aV["cntProbe"])
        
        # CHECK the nighborhoodSize
        if aV["neighbSize"] == 0:
            aV["isTrapped"] = 1
            aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
            print ("WARNING from {}: isTrapped=1, neighbSize={} ..."
                   "no free adjacent coordinates...".format(thisCmd, neighbSize))
            break
        if aV["valueBest"] <= valueTarget:
            step += 1
            aV["walkLength"] = step
            if aV["isWalkTables"]:
                isPivot = 1
                #neighbSize = cntNeighb
                rank = P.coord.rank(aV["coordBest"])
                aWalkProbed[(step,0)] = (step, aV["cntRestart"],
                        aV["coordBest"][:], aV["valueBest"], rank, isPivot,
                        cntNeighb, aV["cntProbe"])
            break
        else:
            # UPDATE coord, value, walkLength
            step += 1
            aV["walkLength"] = step
            coord = coordNext[:]
            value = valueNext

        if aV["cntProbe"] > cntProbeLmt:
            aV["isCensored"] = 1
            aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
            print ("WARNING from {}: isCensored=1, cntProbe={} > cntProbeLmt"
                   "={}\n".format(thisCmd, aV["cntProbe"], aV["cntProbeLmt"]))
            break
        if step == walkLengthLmt:
            aV["isCensored"] = 1
            aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
            print ("WARNING from {}: isCensored=1, step={} > walkLengthLmt"
                   "={}\n".format(thisCmd, step, walkLengthLmt))
            break
        if aV["runtime"] > runtimeLmt:
            aV["isCensored"] = 1
            aV["speedProbe"] = int(aV["cntProbe"]/aV["runtime"])
            print ("WARNING from {}: isCensored=1, runtime={} > runtimeLmt"
                   "={}\n".format(thisCmd, aV["runtime"], aV["runtimeLmt"]))
            break

    if aV["valueBest"] == valueTarget:
        aV["targetReached"] = 1
    elif aV["valueBest"] < valueTarget:
        aV["targetReached"] = 2
    else:
        aV["targetReached"] = 0
    
    return aV["targetReached"]

def stdout( withWarning = 1 ):
    thisCmd = "B.lightp.stdout"
    ABOUT = """This procedure outputs results afer a successful completion of "
             "a combinatorial solver. The output is directed to 'stdout' and includes "
             "a solution (a coordinate-value pair) and the observed performance values. "
             "The format consists of a few comment lines, followed by tabbed "
             "name-value pairs. The first pair is always\n"
             "                     instanceDef <value>\n"
             "This procedure is universal under any function of coordType=P (permutation)!"""
        
    #info global vairables
    global all_info
    global all_value
    global aV
             
    print ("# FROM {}: A SUMMARY OF NAME-VALUE PAIRS"
            "\n# commandLine = {}"
            "\n\n#    dateLine = {}"
            "\n#   timeStamp = {}"
            "\n#".format(thisCmd, aV["commandLine"], aV["dateLine"], aV["timeStamp"]))
             
    stdoutNames = ("instanceDef", "instanceInit", "solverID", "solverMethod", "isSimple",
                    "coordInit", "coordBest", "nDim",
                    "walkLengthLmt", "walkLength", "cntRestartLmt", "cntRestart",
                    "cntProbeLmt", "cntProbe", "runtimeLmt", "runtime", "runtimeRead", "speedProbe", "hostID",
                    "compiler", "walkSegmLmt", "walkSegmCoef", "seedInit", "valueInit",
                    "valueBest", "valueTarget", "valueTol", "targetReached", "isCensored")
             
    for name in stdoutNames:
        if name in aV:
            if name == "solverID":
                print "{}\t\tB.lightp.{}".format(name, aV[name].__name__)
            elif name == "coordInit" or name == "coordBest":
                print "{}\t\t".format(name) + ''.join(imap(str, aV[name]))
            else:
                print "{}\t\t{}".format(name, aV[name])
        else:
            if withWarning:
                print "# WARNING: no value exist for {}".format(name)

def saw_pivot_simple(coordPiv = [1, 1, 1, 1, 0, 1], valuePiv = 3):
    thisCmd = "saw_pivot_simple"
    ABOUT = """This procedure takes a pivot coordinate/value, probes the distance=1 neighborhood of a 'light-out puzzle' (lightp), subject to the constraints of a SAW (self-avoiding walk) -- i.e. the best coord/value it returns has not been et selected as the pivot for the next step. Neighborhood size of 0 signifies that the next step of a SAW is blocked. This implementation is 'simple', i.e. for each pivot coordinate or length L, there are up to L explicit probes of the function f"""
    if coordPiv == "??":
        print ABOUT
        return
    if coordPiv == "?":
        print "Valid query is '" + thisCmd + " ??'"
        return

    #info global variables
    global all_info
    global all_valu
    global aV
    #instance global variables
    global aStruc
    #solver global variables
    global aCoordHash0
    global aWalkedProbed

    try:
        aV["writeVar"] = int(aV["writeVar"])
    except:
        print "writeVar is not an int"

    coordBest = "NA"
    coordBestList = []
    valueProbedList = []
    coordProbedList = []
    valueBest = 2147483641
    neighbSize = 0
    #aV['cntProbe'] = 0
    
    # We take coordPivot and flip the bit from left-to-right,
    # while also extracting neighbor with local valueBest.
    # To make this selection unbiased, we visit neighbors
    # in random order by first permuting aV(varList).
    # NOTE: To maintain a self-avoiding walk, the neighborhood
    # is defined only for coordinates not already used in the walk.
    
    if aV['writeVar'] == 3:
        distance = 0
        rank = B.coord.rank(coordPiv)
        rowLines = "\nA trace from " + thisCmd + ":\nEvaluating neighbors of coordPivot="
        + str(coordPiv)
        + "\ncntProbe\tIdx\tcoordPivot\tvalPivot\tcoordAdj\tvalAdj\tdist\trank\n~\t~\t"
        + str(coordPiv) + "\t" + str(valuePiv) + "\t~\t~\t" + str(distance) + "\t" + str(rank) + "\n"
    
    for var in aV['varList']:
        i = var - 1
        coordAdj = coordPiv[:]
        if coordAdj[i]:
            coordAdj[i] = 0
        else:
            coordAdj[i] = 1
        ##!! To maintain a self-avoiding walk, coordinates from the walk
        ##!! should be excluded from the neighborhood of the current pivot.
        if tuple(coordAdj) not in aCoordHash0:
            neighbSize += 1
            rList = [f(coordAdj)]
            valueAdj = rList[0]
            aV['cntProbe'] += 1
            if aV["isWalkTables"]:
                coordProbedList.append(str(coordAdj))
                valueProbedList.append(valueAdj)
            #!! aggregate coordBestList for random selection later
            if valueAdj <= valueBest:
                if valueAdj < valueBest:
                    coordBestList = []
                valueBest = valueAdj
                coordBest = coordAdj[:]
                coordBestList.append(coordBest)
            if aV['writeVar'] == 3:
                distance = B.coord.distance(coordAdj, coordPiv)
                rank = B.coord.rank(coordAdj)
                rowLines += str(aV['cntProbe']) + "\t" + str(i) + "\t" + str(coordBest) + "\t" + str(valueBest) + "\t" + str(coordAdj) + "\t" + str(rList) + "\t" + str(distance) + "\t" + str(rank) + "\n"
    if aV['writeVar'] == 3:
        print rowLines + "--neighbSize=" + str(neighbSize);
    
    #!! randomize the choice of coordBest from coordBestList
    idx = int(len(coordBestList)*random.random())
    if len(coordBestList) > 0:
        coordBest = coordBestList[idx]
    else:
        coordBest = None
    return (coordBest, valueBest, neighbSize, coordProbedList, valueProbedList)

def saw_pivot(coordPiv=[1,0,1,0,1,0], valuePiv="NA"):
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
    valueBest = sys.maxint
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
    if aV["writeVar"] == 3:
        print "pivotPair = {}:{}".format(coordPiv, valuePiv)
        print aValueAdj
        print aCoordHash0
    
    valueOrderedList = aValueAdj.keys()
    valueOrderedList.sort()
    
    isBestFound = False
    neighbSize = aV["neighbSize"]
    for value in valueOrderedList:
        random.shuffle(aValueAdj[value])
        for coord in aValueAdj[value]:
            if tuple(coord) not in aCoordHash0:
                coordBest = coord
                valueBest = value
                isBestFound = True
            if isBestFound:
                break
            else:
                neighbSize -= 1
        if isBestFound:
            break
    return (coordBest, valueBest, neighbSize)

def patterns(instanceInit=[1, 1, 0, 1, 0, 0], isDebug=0):
    thisCmd="B.lightp.patterns"
    sandbox="B.lightp"
    ABOUT=(
        "\nUSAGE:    {}(\"instanceInit\", isDebug=0)"
        "\n"
        "\nEXAMPLE:  {}(\"110100\")"
        "\n{}(\"110100\",  1)"
        "\n"
        "\nThe command {} takes a binary coordinate 'instanceInit' of length L"
        "\nwhich defines the initial configuration of the 'lights-out puzzle' under"
        "\nthe sandbox {}.  The command initializes and returns the associate"
        "\narray mP(i,j,k) that not only represents the initial state of the puzzle"
        "\nbut also the well-defined patterns of L binary matrices that represent"
        "\nnon-trivial constraints defined for this puzzle."
        "\nFor details, see the interactive 'Lights Out Puzzle Solver' under"
        "\nhttp://www.ueda.info.waseda.ac.jp/~n-kato/lightsout/"
        "\n"
        "\nFor a stdout query, use one of these these commands:"
        "\n{}  ??  (under a tcl shell or a python shell)".format(thisCmd, thisCmd, thisCmd, thisCmd, sandbox, thisCmd))

    if instanceInit == "??":
        print ABOUT
        return
    if instanceInit == "?":
        print "Valid query is '{} ??'".format(thisCmd)
        return

    # compute the number of rows (M) and columns (N) in each of L matrices
    L = len(instanceInit)
    M = int(math.floor(math.sqrt(L)))
    N = int(math.ceil(math.sqrt(L)))

    # In our schema below, the L matrices are indexed by k=(0, 1, 2, ..., L-1)
    # and arranged in M*N grid
    #
    #        k=0[---]          k=1[---]          k=2[---] .....       k=N-1[---]
    #  ...
    #  ...
    #  k=M*(N-1)[---]  k=M*(N-1)+1[---]  k=M*(N-1)+2[---] ..... k=(M*N - 1)[---]
    #

    if L != M * N:
        print """
            ERROR from B.lightp.patterns:
            .. value of L=$L does not factor correctly into  M*N=[expr {$M * $N}]
            .. values of L that would factor correctly are indicated below
                4 6 9 12 16 20 25 30 36 42 49 56 64 72 ...."
            """
        return

    # use instanceInit to initialize mP($i,$j,-1):
    # i.e. the 0-1 matrix selected by random choice or by the user.
    mP = [[[0 for k in xrange(-1, L)] for j in xrange(N)] for i in xrange(M)]

    # print mP

    for i in range(M):
        for j in range(N):
            k = i * N + j
            mP[i][j][-1] = int(instanceInit[k])

    # initialize to value of 0 each of L matrices
    #for k in range(L):
    #    for i in range(M):
    #        for j in range(N):
    #            mP[i][j][k] = 0

    kkMax=L*L
    # initialize the counter variables
    k = -1
    mRow = 0

    i=-1
    j=0
    k=-1

    # assign values of 1 at locations specified for each of L matrices
    for kk in range(kkMax):
        if (kk%L) == 0:
            k += 1
            i = -1# initialize the row counter for each of L matrices
        
        # increment the row counter for each of L matrices
        if (kk%N) == 0:
            i += 1

        # increment the column counter for each of L matrices
        j = kk%N
    
        # periodically, increment the row counter for each group of N matrices
        if (kk%(L*N)) == 0:
            mRow += 1

        if mRow == 1:
            #puts mRow=$mRow...row=$i,col=$j,k=$k
            # case for the left-most matrix of the top row
            if cmp([i, j, k], [0, 0, 0]) == 0:
                mP[0][0][k] = 1
                mP[0][1][k] = 1
                mP[1][0][k] = 1
            # case for the right-most matrix of the top row
            if cmp([i, j, k], [0, N-1, N-1]) == 0:
                mP[0][N-1][k] = 1
                mP[0][N-2][k] = 1
                mP[1][N-1][k] = 1
            # case for matrices in the middle of the top row
            for col in range(1,N-1):
                if cmp([i,j,k], [0,col,col]) == 0:
                    mP[i][j][k]=1
                    mP[i][j-1][k]=1
                    mP[i][j+1][k]=1
                    mP[i+1][j][k]=1

        elif mRow == M:
            #puts mRow=$mRow...row=$i,col=$j,k=$k
            # case for the left-most matrix of the bottom row
            if cmp([i, j, k], [M-1, 0, L-N]) == 0:
                mP[M-1][0][k] = 1
                mP[M-1][1][k] = 1
                mP[M-2][0][k] = 1
            # case for the right-most matrix of the bottom row
            if cmp([i, j, k], [M-1, N-1, L-1]) == 0:
                mP[M-1][N-1][k] = 1
                mP[M-1][N-2][k] = 1
                mP[M-2][N-1][k] = 1
            # case for matrices in the middle of the bottom row
            for col in range(1,N-1):
                if cmp([i,j,k], [M-1,col,L-N+col]) == 0:
                    mP[i][j][k]=1
                    mP[i][j-1][k]=1
                    mP[i][j+1][k]=1
                    mP[i-1][j][k]=1
                    
        else:
            # case for group of middle matrices in the left-most column
            for row in range(1,M-1):
                if cmp([i,j,k],[row,0,N*row]) == 0:
                    mP[i][j][k] = 1
                    mP[i+1][j][k] = 1
                    mP[i-1][j][k] = 1
                    mP[i][j+1][k] = 1
            
            # case for group of middle matrices in the right-most column
            for row in range(1,M-1):
                if cmp([i, j, k], [row, N-1, N*(row+1) - 1]) == 0:
                    mP[i][j][k] = 1
                    mP[i+1][j][k] = 1
                    mP[i-1][j][k] = 1
                    mP[i][j-1][k] = 1
                
            # case for group of middle matrice between left/right columns and top/bottoms rows
            for row in range(1,M-1):
                for col in range(1,N-1):
                    if cmp([i,j,k], [row,col,N*(row) + col]) == 0:
                        mP[i][j][k]=1
                        mP[i+1][j][k]=1
                        mP[i-1][j][k]=1
                        mP[i][j-1][k]=1
                        mP[i][j+1][k]=1

    if isDebug:
        for k in range(L):
            print "k = " + str(k)
            for i in range(M):
                row=[]
                for j in range(N):
                    row.append(mP[i][j][k])
                print row
                                 
    return [M, N, mP]

def patterns_OLD(instanceInit = "110100"):
    thisCmd="B.lightp.patterns"
    ABOUT="""This proc takes ... ."""
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
            k = (i) * N + j
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
    thisCmd = "B.lightp.f"
    ABOUT = """This procedure takes a binary coordinate (passed as an argument) and the"
        "data structure created by procedure  B.lightp.patterns (a matrix passed"
        "in a global array aStruc). It computes and returns the instance function"
        "value, given this coordinate."""
        
    fVal = 0
    isTestOnly = 0
    if aV.has_key('valueTarget') and aV['valueTarget'] == -1:
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
            for i in range(M) :
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

def fAdj(coordPiv = [1,0,1,0,1,0]):
    thisCmd = "B.lightp.fAdj"
    ABOUT = """This procedure takes a pivot coordinate and returns **a COMPLETE set of"
        "adjacent function values**  for the 'light-out puzzle problem' (lightp)."
        "We use a tableau formulation to **efficiently** probe the function not only"
        "with the pivot coordinate but also with **all** of L=M*N adjacent coordinates."
        "Values associated with adjacent coordinates are returned in an associated"
        "array aValueAdj; it can be searched efficiently for coordBest and valueBest"
        "before deciding on the pivotBest for the next step under the rules of"
        "the self-avoiding walk."""
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

    # PASS 1: given coordinate 'coordPiv' and aStruc($i,$j,$k),
    mInit = [x[:] for x in [[0]*N]*M]
    mAdd = [x[:] for x in [[0]*N]*M]
    for i in range(M):
        for j in range(N):
            mInit[i][j] = aStruc[i][j][-1]
            mAdd[i][j] = 0

    for k in range(L):
        isAsserted = coordPiv[k]
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
    aValueAdj = {}
    
    for k in range(L):
        bit = coordPiv[k]
        coordAdj = coordPiv[:]
        #print coordAdj
        if bit:
            coordAdj[k] = 0
        else:
            coordAdj[k] = 1
        valueAdj = 0
        for i in range(M):
            for j in range(N):
                mAdj[i][j] = (mTot[i][j] + aStruc[i][j][k]) % 2
                valueAdj = valueAdj + mAdj[i][j]
        aCoordAdj[tuple(coordAdj)] = valueAdj
        if not aValueAdj.has_key(valueAdj):
            aValueAdj[valueAdj] = []
    
        aValueAdj[valueAdj].append(coordAdj)
    
    aV["cntProbe"] += 1
    if aV["writeVar"] == 3:
        print( "FROM: {}"
              "\nreturning the pivot coordinate:value pair AND ALL ADJACENT"
              "\ncoordinate:value pairs, computed via the tableau method,"
              " cntProbe={}"
              "\n-----\tcoord\tvalue\t-adj-value-from-P.lop.f"
              "\npivot\t{}\t{}\t{}".format(thisCmd, aV["cntProbe"], coordPiv,
                    valuePiv, f(coordPiv)))
    return [valuePiv, aValueAdj]

def exhA(instanceInit = [1, 1, 0, 1, 0, 0]):
    thisCmd = "B_lightp.exhA"
    sandbox = "B.lightp"
    ABOUT=(
           "\nUSAGE:    {}(instanceInit)"
           "\n"
           "\nEXAMPLE:  {}(110100)"
           "\n"
           "\nThe command {} takes a binary coordinate 'instanceInit' of length L"
           "\nwhich defines the initial configuration of the 'lights-out puzzle' under"
           "\nthe sandbox {}. A simple procedure generates a ranked list of"
           "\n2^L binary coordinates to perform an  exhaustive evaluation of the"
           "\n'light-out puzzle' instance as defined by instanceInit; it also returns the"
           "\nminimum value solutions as a list of coordinate:value pairs. The rank of each"
           "\ncoordinate is associated with the Hasse graph representation of the puzzle"
           "\ninstance. For coordinates of lengths L <= 6, the procedure also returns"
           "\na data structure for the follow-up tcl command B.lightp.hasse which creates"
           "\nfiles of vertices and edges for plotting, under R, of SAWs (self-avoiding"
           "\nwalks) in Hasse graphs. For a special case with instanceInit = 000....000"
           "\n(all zeros in the binary string), the self-avoiding walk may demonstrate"
           "\na walk terminated due to a 'trapped pivot'.".format(thisCmd, thisCmd, thisCmd, sandbox))
    global all_info
    global all_valu
    global aV
    global aStruc
    aV = {}
    aStruc = {}
           
    if isinstance(instanceInit, int):
            instanceInit = map(instanceInit, int)
    
    L = len(instanceInit)
    rList = patterns(instanceInit)
    M = rList[0]
    N = rList[1]
    aStruc = rList[2]

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
        value = f(coord)
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
    ABOUT =(
        "\nUSAGE:           {} instanceInit"
        "\n"
        "\nEXAMPLE:         {} 001001011 (under tclsh **OR** python shell)"
        "\n../xBin/B.lightp.exhBT 001001011 (tcl    executable under bash)"
        "\n../xBin/B.lightp.exhBP 001001011 (python executable under bash)"
        "\n"
        "\nThe command {} takes a binary coordinate 'instanceInit' of length L"
        "\nwhich defines the initial configuration of lights-out in the puzzle under"
        "\nthe sandbox {}.  An iterative procedure generates a ranked list of"
        "\n2^L binary coordinates to perform an  exhaustive evaluation of the"
        "\n'light-out puzzle' instance as defined by instanceInit. The principle behind"
        "\nthe iterative coordinate generation is re-use of the associative array"
        "\naCoordHash0. Given this array, the generation proceeds from"
        "\nall coordinates at rank k to all coordinates at rank k+1. The value of k is"
        "\nin the range [0, L]. The exhaustive evaluation includes comprehensive"
        "\ninstrumentation to measure the computational cost and the efficiency of the"
        "\nprocedure."
        "\n"
        "\nFor a stdout query, use one of these these commands:"
        "\n{}  ??  (sourced under tclsh)"
        "\n../xBin/B.lightp.exhBT     (executable under bash)".format(thisCmd, thisCmd, thisCmd, sandbox, thisCmd))
   
    if instanceInit == "??":
        print ABOUT
        return
    if instanceInit == "?":
        print ("Valid query is '{} ??'").format(thisCmd)
        return
    
    if isinstance(instanceInit, basestring):
        instanceInit = map(int, instanceInit)

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
    coordList0 = [coordRef[:]]
    value = B.lightp.f(coordRef)
    valueBest = 1e30
    bestAry = {value: ["000_"+",".join(imap(str,coordRef))+":"+str(value)]}
    coordDistrib = {"000":1}
    sizeTot = 1

    # For each rank, unset aCoordHash0 before aggregating coordList1
    # then probe B.lightp.f for function value
    aCoordHash0 = {}
    coordList1 = []
    runtimeCoord = 0.0
    runtimeProbe = 0.0
    if L <= 5:
        hasseVertices = {(0,1): ["".join(imap(str,coordRef)) + ":" + str(value)] }

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
                coordAdj = coord[:]
                if bit:
                    coordAdj[k] = 0
                else:
                    coordAdj[k] = 1
                weight = B.coord.rank(coordAdj)
                if weight == rank and not ("".join(imap(str,coordAdj)) in aCoordHash0):
                    aCoordHash0["".join(imap(str,coordAdj))] = []
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
            solutionString = "".join(imap(str,coord))+":"+str(value)
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
    print "\nThere are {} valueBest = {} solutions for instanceInit={}\nrank\tsolution".format(len(bestAry[valueMin]), valueMin, ''.join(imap(str,instanceInit)))

    for item in bestAry[valueMin]:
        item = item.split("_")
        rank = item[0]
        solution = item[1]
        print rank+"\t"+solution

    # Output file stuff
    print "\n".join([
        "\n",
        "instanceInit = {}, M = {} (rows), N = {} (columns)".format(''.join(imap(str,instanceInit)), M, N),
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

    return

#if __name__ == "__main__":
