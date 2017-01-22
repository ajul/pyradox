import _initpath
import os
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.format
import pyradox.struct
import pyradox.txt
import pyradox.wiki

from unitstats import computeUnitType, computeUnitName

units = pyradox.hoi4.unit.getUnits()["sub_units"]

terrains = pyradox.txt.parseFile(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'terrain', '00_terrain.txt'), verbose=False)['categories']

landTerrainKeys = [key for key, value in terrains.items() if "movement_cost" in value and not value["is_water"]]

def computeIsSupport(unit):
    return unit["group"] == "support"

def computeUnitTerrainStat(unit, terrainKey, statKey):
    if terrainKey in unit:
        return unit[terrainKey][statKey] or 0.0
    return 0.0

def coloredPercentString(x):
    if x > 0.0:
        return "{{green|%+d%%}}" % round(x * 100.0)
    elif x < 0.0:
        return "{{red|%+d%%}}" % round(x * 100.0)
    else:
        return ""

def computeUnitStatFunction(terrainKey, statKey):
    if terrainKey in terrains and "units" in terrains[terrainKey]:
        baseModifier = terrains[terrainKey]["units"][statKey] or 0.0
    else:
        baseModifier = 0.0
    def resultFunction(unitKey, unit):
        result = computeUnitTerrainStat(unit, terrainKey, statKey)
        return coloredPercentString(result)
    return resultFunction

def computeSmallRiverStatFunction(statKey):
    if statKey == "attack": baseModifier = -0.3
    elif statKey == "movement": baseModifier = -0.25
    else: baseModifier = 0.0
    def resultFunction(unitKey, unit):
        result = computeUnitTerrainStat(unit, "river", statKey)
        # if statKey != "defence": result = min(result, 0)
        return coloredPercentString(result)
    return resultFunction

def computeLargeRiverStatFunction(statKey):
    if statKey == "attack": baseModifier = -0.6
    elif statKey == "movement": baseModifier = -0.5
    else: baseModifier = 0.0
    def resultFunction(unitKey, unit):
        result = computeUnitTerrainStat(unit, "river", statKey)
        # if statKey != "defence": result = min(result, 0)
        return coloredPercentString(result)
    return resultFunction

def computeAmphibiousStatFunction(statKey):
    if statKey == "attack": baseModifier = -0.7
    else: baseModifier = 0.0
    def resultFunction(unitKey, unit):
        result = computeUnitTerrainStat(unit, "amphibious", statKey)
        # if statKey != "defence": result = min(result, 0)
        return coloredPercentString(result)
    return resultFunction

def makeColumns(statKey, includeLast = True):
    result = (
        [("Unit", computeUnitName),
         ("Type", lambda k, v: "Support" if computeIsSupport(v) else "Combat"),
         ] +
        [(terrainKey.title(), computeUnitStatFunction(terrainKey, statKey), None) for terrainKey in landTerrainKeys] +
        [
            ("Small river", computeSmallRiverStatFunction(statKey), None),
            ("Large river", computeLargeRiverStatFunction(statKey), None)])
    if includeLast:
        result += [
            ("Amphibious", computeAmphibiousStatFunction(statKey), None),
            ("Fort", computeUnitStatFunction("fort", statKey), None)]
    return result

file = open("out/unit_terrain.txt", "w")

file.write("=== Attack ===\n")
file.write(pyradox.wiki.makeWikitable(units, makeColumns("attack"),
                                      filterFunction = lambda k, v: computeUnitType(v) == "land",
                                      sortFunction = lambda item: computeUnitName(item[0])))
file.write("=== Defense ===\n")
file.write(pyradox.wiki.makeWikitable(units, makeColumns("defence"),
                                      filterFunction = lambda k, v: computeUnitType(v) == "land",
                                      sortFunction = lambda item: computeUnitName(item[0])))
file.write("=== Movement ===\n")
file.write(pyradox.wiki.makeWikitable(units, makeColumns("movement"),
                                      filterFunction = lambda k, v: computeUnitType(v) == "land",
                                      sortFunction = lambda item: computeUnitName(item[0])))

file.close()
