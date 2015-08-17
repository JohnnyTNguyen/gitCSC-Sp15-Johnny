import os
import time
import glob
import importlib
import sys

isVerbose = False
thisFile = "all_python"

workDir = os.path.dirname(os.path.realpath(__file__))
thisDir = os.path.dirname(os.path.realpath(__file__))
sys.path.extend([os.path.dirname(workDir) + "/pLib"])

print ".. importing files from this SANDBOX directory \n{}".format(thisDir)

thisDir = "../../../xBed/pLib"
os.chdir(thisDir)
thisDir = os.getcwd()
sys.path.extend([thisDir])

print ".. importing files from xBed/pLib directory \n{}".format(thisDir)

os.chdir(workDir)
print ".. returning to directory \n{}".format(workDir)
print time.strftime("%a %b %d %H:%M:%S %Z %Y")

from config import *
#sys.path.extend(["./pLib","../../../xBed/pLib"])

thisDir = workDir
sandboxPath = os.path.dirname(thisDir) 
sandboxName = os.path.basename(sandboxPath)
infoVariablesFile = sandboxName + ".info_variables.txt"
infoVariablesFile = "/".join([sandboxPath,"pLib",infoVariablesFile])

if os.path.isfile(infoVariablesFile):
    all_info["sandboxName"] = sandboxName
    all_info["sandboxPath"] = sandboxPath
    all_info["infoVariablesFile"] = infoVariablesFile
    print ".. registered infoVariablesFile as {}".format(infoVariablesFile)
else:
    # Error
    print "\n".join([
        "",
        "ERROR from {}".format(thisFile),
        ".. missing the infoVariablesFile as {}".format(infoVariablesFile)
        ])

import B
import util
import core
