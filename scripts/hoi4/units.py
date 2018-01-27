import _initpath
import load.tech
import load.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki
import os.path

from unitstats import *

files = {}
for unit_type in base_columns.keys():
    files[unit_type] = open("out/%s_units.txt" % unit_type, "w")

columns = {
    "land" : (
        ("Unit", compute_unit_name),
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

for unit_type, unit_file in files.items():
    unit_file.write(pyradox.wiki.make_wikitable(units, columns[unit_type],
                                              filter_function = lambda k, v: compute_unit_type(v) == unit_type, collapse = True,
                                              sort_function = lambda key, value: compute_unit_name(key)))
    #unit_file.write("=== Derived statistics ===\n")
    #unit_file.write(pyradox.wiki.make_wikitable(units, derived_columns[unit_type], lambda k, v: compute_unit_type(v) == unit_type and is_availiable(v)))

for unit_file in files.values():
    unit_file.close()
