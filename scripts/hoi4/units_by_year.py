import _initpath
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki
import pyradox.yml
import os.path
import json

import unitstats

allYears = pyradox.struct.Tree()

unitType = 'land'

for year in unitstats.unitTypeYears[unitType]:
    units = unitstats.unitsAtYear(year)
    allYears += units

with open("out/%s_units_by_year.txt" % unitType, "w") as outFile:
    columns = [("Unit", unitstats.computeUnitName)] + unitstats.baseColumns[unitType] + [("Unit", unitstats.computeUnitName)]
    tables = {year : pyradox.struct.Tree() for year in unitstats.unitTypeYears[unitType]}
    for unitKey, unit in allYears.items():
        if unit["year"] in unitstats.unitTypeYears[unitType] and unitstats.computeUnitType(unit) == unitType and unitstats.isAvailiable(unit):
            tables[unit["year"]].append(unitKey, unit)
    for year in unitstats.unitTypeYears[unitType]:
        outFile.write("== %d ==\n" % year)
        outFile.write(pyradox.wiki.makeWikitable(tables[year], columns,
                                                 sortFunction = lambda item: unitstats.computeUnitName(item[0])))

with open("out/%s_units_by_unit.txt" % unitType, "w") as outFile:
    columns = [("Year", "%(year)d")] + unitstats.baseColumns[unitType]
    tables = {}
    for unitKey, unit in allYears.items():
        if unit["year"] not in unitstats.unitTypeYears[unitType]: continue
        if unitstats.computeUnitType(unit) == unitType and unitstats.isAvailiable(unit) and unit["last_upgrade"] == unit["year"]:
            if unitKey not in tables: tables[unitKey] = pyradox.struct.Tree()
            tables[unitKey].append(unit["year"], unit)
    for unitKey, unitYears in sorted(tables.items(), key=lambda item: unitstats.computeUnitName(item[0])):
        unitName = unitstats.computeUnitName(unitKey)
        outFile.write("== %s ==\n" % unitName)
        outFile.write(pyradox.wiki.makeWikitable(unitYears, columns, sortable=False))



jsonOut = open("out/%s_years.json" % unitType,"w")
dataForJSON = {year : {} for year in unitstats.unitTypeYears[unitType]}
for unitKey, unit in allYears.items():
    if unit["year"] in unitstats.unitTypeYears[unitType] and unitstats.computeUnitType(unit) == unitType and unitstats.isAvailiable(unit):
        dataForJSON[unit["year"]][unitKey] = {}
        for column in unitstats.baseColumns[unitType] :
            keyName, contents = column[0], column[1]
            if callable(contents):
                try:
                    contentString = contents(unitKey, unit)
                except ZeroDivisionError:
                    contentString = ''
            elif contents is None:
                contentString = pyradox.format.humanString(key, True)
            else:
                try:
                    contentString = contents % unit
                except TypeError:
                    contentString = ''

            dataForJSON[unit["year"]][unitKey][keyName] = contentString

jsonOut.write(json.dumps(dataForJSON,indent=2,sort_keys=True))

#CSV output one file per year
columns = []
for column in unitstats.baseColumns[unitType] :
    columns.append(column[0]);
columns.sort()
printColumns = ["Unit"] + columns
str = ","
for year in dataForJSON:
    csvOut = open("out/%s_%s.csv" % (unitType, year),"w")
    csvOut.write(str.join(printColumns) + "\n")
    if(len(dataForJSON[year].keys())):
        for unit in sorted(dataForJSON[year]):
            data = [unit]
            for column in columns:
                data.append(dataForJSON[year][unit][column])
            csvOut.write(str.join(data) + "\n")

