import _initpath
import os
import re
import io
import collections
import pyradox
import warnings

warnings.simplefilter("ignore", pyradox.txt.ParseWarning)
savetree = pyradox.parse_file('in/1820.eu4')

print(sum(x for x in savetree.find_walk("losses") if isinstance(x, int)))
