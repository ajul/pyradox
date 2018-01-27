import _initpath
import load.tech
import load.unit

import pyradox


from unitstats import *

files = {}
for unit_type in base_columns.keys():
    files[unit_type] = open("out/%s_units_by_year.txt" % unit_type, "w")

for year in range(1936, 1948):
    units = units_at_year(year)

    for unit_type, unit_file in files.items():
        unit_file.write("== %d ==\n" % year)
        unit_file.write(pyradox.wiki.make_wikitable(units, base_columns[unit_type], lambda k, v: v["type"] == unit_type and v["active"]))
        unit_file.write("=== Derived statistics ===\n")
        unit_file.write(pyradox.wiki.make_wikitable(units, derived_columns[unit_type], lambda k, v: v["type"] == unit_type and v["active"]))

for unit_file in files.values():
    unit_file.close()
