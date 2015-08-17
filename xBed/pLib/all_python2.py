thisDir = "../../../xBed/pLib" 
os.chdir(thisDir)
thisDir = os.getcwd()
sys.path.extend([thisDir])
"""
print ".. importing python files from the xBed directory \n{}".format(thisDir)
moduleList = glob.glob("*.py")
for module in moduleList:
    if "all_python" not in module:
        print ".. importing module {}".format(module)
        if "core" in module:
            core = importlib.import_module(module[:-3])
        if "util" in module:
            util = importlib.import_module(module[:-3])
"""
