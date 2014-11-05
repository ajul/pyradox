import _initpath
import os
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.primitive
import pyradox.image
import pyradox.struct

startDate = pyradox.primitive.Date('1444.11.11')

counts = pyradox.struct.Tree() # province counts

# parse all files in a directory, producing instances of pyradox.struct.Tree
for filename, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'history', 'provinces')):
    # pyradox.struct.Tree has many dict methods, such as .keys()
    if 'base_tax' not in data.keys(): continue
    
    tradeGood = 'unknown'
    for currGood in data.findWalk('trade_goods'):
        if currGood != 'unknown':
            tradeGood = currGood
        
    if tradeGood not in counts: counts[tradeGood] = 1
    else: counts[tradeGood] += 1
        
print([(key, counts[key]) for key in counts.keys()])
