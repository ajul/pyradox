import os
import re
import io
import collections
import pyradox
import warnings

import cProfile
import pstats

warnings.simplefilter("ignore", pyradox.txt.ParseWarning)
pr = cProfile.Profile()

pr.enable()
savetree = pyradox.parseFile('in/thebloke.eu4')
print(savetree["checksum"])
pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('time')
ps.print_stats()
print(s.getvalue())
