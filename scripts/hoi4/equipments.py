import _initpath
import load.tech
import load.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki

from unitstats import *

files = {}
for unit_type in base_columns.keys():
    files[unit_type] = open("out/%s_equipments_by_year.txt" % unit_type, "w")

for unit_type, unit_file in files.items():
    unit_file.write(pyradox.wiki.make_wikitable(equipments, equipment_columns[unit_type],
                                              filter_function = lambda k, v: ('year' in v or v['active']) and compute_equipment_type(v) == unit_type))

for unit_file in files.values():
    unit_file.close()
