import _initpath
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki

from unitstats import *

files = {}
for unitType in baseColumns.keys():
    files[unitType] = open("out/%s_equipments_by_year.txt" % unitType, "w")

for unitType, unitFile in files.items():
    unitFile.write(pyradox.wiki.makeWikitable(equipments, equipmentColumns[unitType],
                                              filterFunction = lambda k, v: ('year' in v or v['active']) and computeEquipmentType(v) == unitType))

for unitFile in files.values():
    unitFile.close()
