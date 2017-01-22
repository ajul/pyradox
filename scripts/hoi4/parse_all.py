import _initpath
import os
import re
import sys
import pyradox.config
import pyradox.txt

def parseWalk(dirname, verbose=False):
    """Given a directory, recursively iterate over the content of the .txt files in that directory as Trees"""
    
skip = '\\\\(map|wiki|interface|pdx_launcher|previewer_assets)\\\\'


dirname = os.path.join(pyradox.config.getBasedir('HoI4'))
for root, dirs, files in os.walk(dirname):
    if root == dirname: continue
    for filename in files:
        fullpath = os.path.join(root, filename)
        _, ext = os.path.splitext(fullpath)
        if ext == ".txt" and not re.search(skip, fullpath):
            try:
                pyradox.txt.parseFile(fullpath)
            except:
                print(sys.exc_info())
