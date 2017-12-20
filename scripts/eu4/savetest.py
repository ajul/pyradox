import _initpath
import os
import re
import io
import collections
import pyradox
import warnings

import c_profile
import pstats

import time

mode = "profiler"

class Timer:    
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start

warnings.simplefilter("ignore", pyradox.txt.ParseWarning)

if mode == "profiler":
    pr = c_profile.Profile()

    pr.enable()
    savetree = pyradox.parse_file('in/thebloke.eu4')
    print(savetree["checksum"])
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('time')
    ps.print_stats()
    print(s.getvalue())
else:
    with Timer() as t:
        savetree = pyradox.parse_file('in/thebloke.eu4')
        print(savetree["checksum"])
    print("Elapsed time: %fs" % t.interval)
