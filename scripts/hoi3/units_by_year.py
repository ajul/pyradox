import _initpath
import pyradox.hoi3.tech
import pyradox.hoi3.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki

from unitstats import *

files = {}
for unitType in baseColumns.keys():
    files[unitType] = open("out/%s_units_by_year.txt" % unitType, "w")

for year in range(1936, 1948):
    units = unitsAtYear(year)

    for unitType, unitFile in files.items():
        unitFile.write("== %d ==\n" % year)
        unitFile.write(pyradox.wiki.makeWikitable(units, baseColumns[unitType], lambda k, v: v["type"] == unitType and v["active"]))
        unitFile.write("=== Derived statistics ===\n")
        unitFile.write(pyradox.wiki.makeWikitable(units, derivedColumns[unitType], lambda k, v: v["type"] == unitType and v["active"]))

for unitFile in files.values():
    unitFile.close()
