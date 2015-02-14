import copy
import os
import pyradox.format
import pyradox.txt
import pyradox.struct
import pyradox.config

# helper functions for loading directory contents 

cache = {}

def loadFunctions(gameName, name, dirpath, mode = None):
    if isinstance(dirpath, str): dirpath = (dirpath,)
    def parseData(basedir = None):
        if basedir is None: basedir = pyradox.config.basedirs[gameName]

        if mode == "merge":
            result = pyradox.txt.parseMerge(os.path.join(basedir, *dirpath))
        elif mode == "walk":
            result = pyradox.struct.Tree()
            for filename, tree in pyradox.txt.parseWalk(os.path.join(basedir, *dirpath)):
                tag, rawName = pyradox.format.splitFilename(filename)
                result.append(tag, tree)
        else:
            result = pyradox.struct.Tree()
            for filename, tree in pyradox.txt.parseDir(os.path.join(basedir, *dirpath)):
                tag, rawName = pyradox.format.splitFilename(filename)
                result.append(tag, tree)
            
        print('Loaded %s.' % name)
        return result

    def getData(basedir = None):
        if basedir is None: basedir = pyradox.config.basedirs[gameName]
        if basedir not in cache: cache[basedir] = {}
        if name not in cache[basedir]: cache[basedir][name] = parseData(basedir)
        return copy.deepcopy(cache[basedir][name])

    return parseData, getData
