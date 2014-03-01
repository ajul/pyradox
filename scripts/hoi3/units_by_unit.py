import _initpath
import pyradox.hoi3.tech
import pyradox.hoi3.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki

from unitstats import *

files = {}
for unitType in baseColumns.keys():
    files[unitType] = open("out/%s_units_by_unit.txt" % unitType, "w")

unitData = {}

for year in range(1936, 1948):
    unitData[year] = unitsAtYear(year)

byUnit = pyradox.struct.Tree()

for year, data in unitData.items():
    for unit, stats in data.items():
        if unit not in byUnit.keys(): byUnit[unit] = pyradox.struct.Tree()
        byUnit[unit][year] = stats

for unitType, unitFile in files.items():
    for unit, data in byUnit.items():
        if data[1936]["type"] != unitType: continue
        unitFile.write("== %s ==\n" % pyradox.format.humanString(unit, True))
        unitFile.write(pyradox.wiki.makeWikitable(data, baseColumns[unitType], lambda k, v: v["active"]))
        unitFile.write("=== Derived statistics ===\n")
        unitFile.write(pyradox.wiki.makeWikitable(data, derivedColumns[unitType], lambda k, v: v["active"]))

for unitFile in files.values():
    unitFile.close()
