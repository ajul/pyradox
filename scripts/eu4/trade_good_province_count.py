import _initpath
import os
import re
import collections

import pyradox

import pyradox.image
import pyradox

start_date = pyradox.Date('1444.11.11')

counts = pyradox.Tree() # province counts

# parse all files in a directory, producing instances of pyradox.Tree
for filename, data in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('EU4'), 'history', 'provinces')):
    # pyradox.Tree has many dict methods, such as .keys()
    if 'base_tax' not in data.keys(): continue
    
    trade_good = 'unknown'
    for curr_good in data.find_walk('trade_goods'):
        if curr_good != 'unknown':
            trade_good = curr_good
        
    if trade_good not in counts: counts[trade_good] = 1
    else: counts[trade_good] += 1
        
print([(key, counts[key]) for key in counts.keys()])
