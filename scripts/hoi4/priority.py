import _initpath
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki
import os.path

from unitstats import *

f = open("out/priority.txt", "w")

columns = (
    ("Unit", computeUnitName),
    ("Priority", "%(priority)d"),
    ("Type", lambda k, v: '<br/>'.join(v['type'])),
    )

f.write(pyradox.wiki.makeWikitable(units, columns,
                                          filterFunction = lambda k, v: computeUnitType(v) == "land", collapse = True,
                                          sortFunction = lambda item: computeUnitName(item[0])))
f.close()
