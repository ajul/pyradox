import _initpath
import os
import re
import io
import collections
import pyradox
import warnings

warnings.simplefilter("ignore", pyradox.txt.ParseWarning)
savetree = pyradox.parseFile('in/1820.eu4')

print(sum(x for x in savetree.findWalk("losses") if isinstance(x, int)))
