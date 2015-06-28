import sys
import os
import time
from subprocess import call

def whoami():
    print call("whoami")[0]

def date():
    print time.strftime("%c")
    
def cd(path):
    os.chdir(path)

def pwd():
    full_path = os.path.realpath(__file__)
    file_dir = os.path.dirname(full_path)
    print file_dir
     
def file_read(fileName):
    data = ""
    try:
        f = file(fileName,'r')
        data = f.read()
        f.close()
    except IOError as e:
        sys.stderr.write("Error: {}\n".format(e.strerror))
        sys.exit(1)
    
    return data
    
def file_write(fileName, data):
    try:
        f = file(fileName,'a')
        f.write(data)
        f.close()
    except IOError as e:
        sys.stderr.write("Error: {}\n".format(e.strerror))
        sys.exit(1)
