import _initpath
import load.tech
import load.unit
import pyradox
import os.path
import json

import unitstats

all_years = pyradox.Tree()

unit_type = 'land'

for year in unitstats.unit_type_years[unit_type]:
    units = unitstats.units_at_year(year)
    all_years += units

with open("out/%s_units_by_year.txt" % unit_type, "w") as out_file:
    columns = [("Unit", unitstats.compute_unit_name)] + unitstats.base_columns[unit_type] + [("Unit", unitstats.compute_unit_name)]
    tables = {year : pyradox.Tree() for year in unitstats.unit_type_years[unit_type]}
    for unit_key, unit in all_years.items():
        if unit["year"] in unitstats.unit_type_years[unit_type] and unitstats.compute_unit_type(unit) == unit_type and unitstats.is_availiable(unit):
            tables[unit["year"]].append(unit_key, unit)
    for year in unitstats.unit_type_years[unit_type]:
        out_file.write("== %d ==\n" % year)
        out_file.write(pyradox.wiki.make_wikitable(tables[year], columns,
                                                 sort_function = lambda key, value: unitstats.compute_unit_name(key)))

with open("out/%s_units_by_unit.txt" % unit_type, "w") as out_file:
    columns = [("Year", "%(year)d")] + unitstats.base_columns[unit_type]
    tables = {}
    for unit_key, unit in all_years.items():
        if unit["year"] not in unitstats.unit_type_years[unit_type]: continue
        if unitstats.compute_unit_type(unit) == unit_type and unitstats.is_availiable(unit) and unit["last_upgrade"] == unit["year"]:
            if unit_key not in tables: tables[unit_key] = pyradox.Tree()
            tables[unit_key].append(unit["year"], unit)
    for unit_key, unit_years in sorted(tables.items(), key=lambda key, value: unitstats.compute_unit_name(key)):
        unit_name = unitstats.compute_unit_name(unit_key)
        out_file.write("== %s ==\n" % unit_name)
        out_file.write(pyradox.wiki.make_wikitable(unit_years, columns, sortable=False))



json_out = open("out/%s_years.json" % unit_type,"w")
data_for_json = {year : {} for year in unitstats.unit_type_years[unit_type]}
for unit_key, unit in all_years.items():
    if unit["year"] in unitstats.unit_type_years[unit_type] and unitstats.compute_unit_type(unit) == unit_type and unitstats.is_availiable(unit):
        data_for_json[unit["year"]][unit_key] = {}
        for column in unitstats.base_columns[unit_type] :
            key_name, contents = column[0], column[1]
            if callable(contents):
                try:
                    content_string = contents(unit_key, unit)
                except ZeroDivisionError:
                    content_string = ''
            elif contents is None:
                content_string = pyradox.format.human_string(key, True)
            else:
                try:
                    content_string = contents % unit
                except TypeError:
                    content_string = ''

            data_for_json[unit["year"]][unit_key][key_name] = content_string

json_out.write(json.dumps(data_for_json,indent=2,sort_keys=True))

#CSV output one file per year
columns = []
for column in unitstats.base_columns[unit_type] :
    columns.append(column[0]);
columns.sort()
print_columns = ["Unit"] + columns
str = ","
for year in data_for_json:
    csv_out = open("out/%s_%s.csv" % (unit_type, year),"w")
    csv_out.write(str.join(print_columns) + "\n")
    if(len(data_for_json[year].keys())):
        for unit in sorted(data_for_json[year]):
            data = [unit]
            for column in columns:
                data.append(data_for_json[year][unit][column])
            csv_out.write(str.join(data) + "\n")

