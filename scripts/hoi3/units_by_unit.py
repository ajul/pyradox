import _initpath
import load.tech
import load.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki

from unitstats import *

files = {}
for unit_type in base_columns.keys():
    files[unit_type] = open("out/%s_units_by_unit.txt" % unit_type, "w")

unit_data = {}

for year in range(1936, 1948):
    unit_data[year] = units_at_year(year)

by_unit = pyradox.struct.Tree()

for year, data in unit_data.items():
    for unit, stats in data.items():
        if unit not in by_unit.keys(): by_unit[unit] = pyradox.struct.Tree()
        by_unit[unit][year] = stats

for unit_type, unit_file in files.items():
    for unit, data in by_unit.items():
        if data[1936]["type"] != unit_type: continue
        unit_file.write("== %s ==\n" % pyradox.format.human_string(unit, True))
        unit_file.write(pyradox.wiki.make_wikitable(data, base_columns[unit_type], lambda k, v: v["active"]))
        unit_file.write("=== Derived statistics ===\n")
        unit_file.write(pyradox.wiki.make_wikitable(data, derived_columns[unit_type], lambda k, v: v["active"]))

for unit_file in files.values():
    unit_file.close()
