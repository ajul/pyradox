import _initpath
import load.tech
import load.unit

import pyradox

import os.path

from unitstats import *

f = open("out/priority.txt", "w")

columns = (
    ("Unit", compute_unit_name),
    ("Priority", "%(priority)d"),
    ("Type", lambda k, v: '<br/>'.join(v['type'])),
    )

f.write(pyradox.wiki.make_wikitable(units, columns,
                                          filter_function = lambda k, v: compute_unit_type(v) == "land", collapse = True,
                                          sort_function = lambda key, value: compute_unit_name(key)))
f.close()
