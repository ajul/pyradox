import _initpath
import os
import sys
import pyradox.config
import pyradox.txt

def parseWalk(dirname, verbose=False):
    """Given a directory, recursively iterate over the content of the .txt files in that directory as Trees"""
    

dirname = os.path.join(pyradox.config.basedirs['HoI4'])
for root, dirs, files in os.walk(dirname):
    if root == dirname: continue
    for filename in files:
        fullpath = os.path.join(root, filename)
        _, ext = os.path.splitext(fullpath)
        if ext == ".txt":
            try:
                pyradox.txt.parseFile(fullpath)
            except:
                print(sys.exc_info())
