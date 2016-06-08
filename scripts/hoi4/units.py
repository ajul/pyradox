import _initpath
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki
import os.path

from unitstats import *

files = {}
for unitType in baseColumns.keys():
    files[unitType] = open("out/%s_units.txt" % unitType, "w")

columns = {
    "land" : (
        ("Unit", computeUnitName),
        ("Year", "%(year)d"),
        ("Manpower", "%(manpower)d"),
        ("Training time", "%(training_time)d"),
        ("Organization", "%(max_organisation)d"),
        ("Recovery rate", "%(default_morale)0.1f"),
        ("HP", "%(max_strength)d"),
        ("Combat width", "%(combat_width)d"),
        ("Suppression", "%(suppression)d"),
        ("Weight", "%(weight)0.1f"),
        ),
    "naval" : (
        ("Unit", None),
        ),
    "air" : (
        ("Unit", None),
        )
    }

for unitType, unitFile in files.items():
    unitFile.write(pyradox.wiki.makeWikitable(units, columns[unitType],
                                              filterFunction = lambda k, v: computeUnitType(v) == unitType, collapse = True,
                                              sortFunction = lambda item: computeUnitName(item[0])))
    #unitFile.write("=== Derived statistics ===\n")
    #unitFile.write(pyradox.wiki.makeWikitable(units, derivedColumns[unitType], lambda k, v: computeUnitType(v) == unitType and isAvailiable(v)))

for unitFile in files.values():
    unitFile.close()
