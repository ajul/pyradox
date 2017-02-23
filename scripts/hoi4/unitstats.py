import _initpath
import re
import pyradox.format
import pyradox.struct
import pyradox.hoi4.equipment
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.yml

factoriesPerResource = 1.5 / 8.0

defaultYear = 1918

techs = pyradox.hoi4.tech.getTechs()["technologies"]
equipments = pyradox.hoi4.equipment.getEquipments()["equipments"]
units = pyradox.hoi4.unit.getUnits()["sub_units"]

for equipmentKey, equipmentValue in equipments.items():
    if "archetype" in equipmentValue:
        equipmentValue.weakUpdate(equipments[equipmentValue["archetype"]])
        equipmentValue["is_archetype"] = False
        
for techKey, tech in techs.items():
    if not isinstance(tech, pyradox.struct.Tree): continue
    year = tech["start_year"] or defaultYear
    if "enable_equipments" in tech:
        for equipmentKey in tech.findAll("enable_equipments"):
            equipment = equipments[equipmentKey]
            equipment['year'] = year
    if "enable_subunits" in tech:
        for unitKey in tech.findAll("enable_subunits"):
            units[unitKey]["year"] = year

def unitsAtYear(year):
    units = pyradox.hoi4.unit.getUnits()["sub_units"]
    
    # archetypeKey -> best equipment
    equipmentModels = {}
    
    for unitKey, unitData in units.items():
        unitData["year"] = year
        unitData["last_upgrade"] = defaultYear
        if "active" not in unitData.keys(): unitData["active"] = True
    
    for techKey, tech in techs.items():
        if not isinstance(tech, pyradox.struct.Tree): continue
        if (tech["start_year"] or year) > year: continue
        if tech["allow"] and tech["allow"]["always"] == False: continue # ignore unallowed techs
        if 'folder' in tech and 'doctrine' in tech['folder']['name']: continue # ignore doctrines
        if "enable_equipments" in tech:
            for equipmentKey in tech.findAll("enable_equipments"):
                equipment = equipments[equipmentKey]
                if "archetype" in equipment:
                    archetypeKey = equipment["archetype"]
                    equipmentModels[archetypeKey] = equipments[equipmentKey]
                equipmentModels[equipmentKey] = equipments[equipmentKey]
                # TODO: drop ordering assumption?
        if "enable_subunits" in tech:
            for unitKey in tech.findAll("enable_subunits"):
                units[unitKey]["active"] = True
                units[unitKey]["last_upgrade"] = max(units[unitKey]["last_upgrade"], tech["start_year"])

        # non-equipment modifiers
        for unitKey, unitData in units.items():
            for techUnitKey, stats in tech.items():
                if techUnitKey == unitKey or techUnitKey in unitData.findAll('categories'):
                    units[unitKey]["last_upgrade"] = max(units[unitKey]["last_upgrade"], tech["start_year"])
                    for statKey, statValue in stats.items():
                        if (not type(statValue) is pyradox.Tree):
                            unitData[statKey] = (unitData[statKey] or 0.0) + statValue

    # fill in equipment
    for unitKey, unitData in units.items():
        unitData["equipments"] = pyradox.struct.Tree()
        for archetypeKey in unitData["need"]:
            if archetypeKey in equipmentModels:
                equipment = equipmentModels[archetypeKey]
                unitData["equipments"][archetypeKey] = equipment
                unitData["last_upgrade"] = max(unitData["last_upgrade"], equipment["year"])
                if not equipments[archetypeKey]["is_archetype"]:
                    print("Warning: non-archetype equipment %s defined for %s" % (archetypeKey, unitKey))
            else:
                unitData["equipments"][archetypeKey] = False
        
    return units

def computeUnitName(unitKey, unit = None):
    return pyradox.yml.getLocalization(unitKey, ['unit'], game = 'HoI4') or pyradox.format.humanString(unitKey)
    
def computeUnitType(unit):
    if unit["map_icon_category"] == "ship":
        return "naval"
    elif unit["map_icon_category"] is None:
        return "air"
    else:
        return "land"
        
def computeEquipmentType(equipment):
    if 'air_range' in equipment:
        return 'air'
    elif 'port_capacity_usage' in equipment:
        return 'naval'
    else:
        return 'land'

def isAvailiable(unit):
    for equipmentKey, equipment in unit["equipments"].items():
        if equipment is False:
            return False
    return unit["active"]

def computeUnitCost(unitKey, unitData):
    result = 0
    for archetypeKey, quantity in unitData["need"].items():
        equipment = unitData["equipments"][archetypeKey]
        result += quantity * equipment["build_cost_ic"]
    return "%d" % result

def computeUnitResourceCost(unitKey, unitData):
    result = 0
    for archetypeKey, quantity in unitData["need"].items():
        equipment = unitData["equipments"][archetypeKey]
        if "resources" not in equipment: continue
        result += quantity * sum(equipment["resources"].values()) * equipment["build_cost_ic"]
    return "%d" % result

def computeUnitTotalCost(unitKey, unitData):
    result = 0
    for archetypeKey, quantity in unitData["need"].items():
        equipment = unitData["equipments"][archetypeKey]
        if "resources" not in equipment: continue
        result += quantity * (equipment["build_cost_ic"]
                              + factoriesPerResource * sum(equipment["resources"].values()) * equipment["build_cost_ic"])
    return "%d" % result
    
def computeEquipmentCost(equipmentKey, equipment):
    return '%d' % equipment['build_cost_ic']
    
def computeEquipmentResourceCost(equipmentKey, equipment):
    if "resources" not in equipment: return '0'
    return '%d' % (sum(equipment["resources"].values()) * equipment['build_cost_ic'])
    
def computeEquipmentTotalCost(equipmentKey, equipment):
    result = equipment['build_cost_ic']
    if "resources" in equipment: result *= (1.0 + factoriesPerResource * sum(equipment["resources"].values()))
    return '%d' % result

def computeUnitStatFunction(statKey, formatString = "%0.1f", combiner = sum, baseValue = None, displayZero = False, usePercent = False):
    def resultFunction(unitKey, unitData):
        def getStats():
            if baseValue is not None: yield baseValue
            for equipment in unitData["equipments"].values():
                if statKey in equipment:
                    yield equipment[statKey]
    
        result = combiner(getStats()) * (1.0 + (unitData[statKey] or 0.0))
        
        if result == 0.0 and not displayZero: return ''
        else: 
            if usePercent:
                return re.sub('%.*?[df]', '\g<0>%%', formatString) % (result * 100.0)
            else:
                return formatString % result

    return resultFunction
    
def equipmentName(key, value):
    tokens = key.split('_')
    result = ''
    for token in tokens:
        if token == 'equipment': continue
        if token == '1': token = 'I'
        if token == '2': token = 'II'
        if token == '3': token = 'III'
        if token == '4': token = 'IV'
        if token == 'cv': token = 'carrier'
        result += token + ' '
    result = result[0].upper() + result[1:-1]
    return result
    
def computeNavalMaxStrength(equipmentKey, equipment):
    if 'max_strength' in equipment:
        return '%d' % equipment['max_strength']
    for i in range(len(equipmentKey)):
        if equipmentKey[0:i] in units:
            return '%d' % units[equipmentKey[0:i]]['max_strength']

unitTypeYears = {
    "land" : [1918, 1934, 1936, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945],
    "naval" : [1922, 1936, 1940, 1944],
    "air" : [1933, 1936, 1940, 1944, 1945, 1950],
}
    
baseColumns = {
    "land" : [
        ("Prod. cost", computeUnitCost),
        ("Res. cost", computeUnitResourceCost),
        ("Total cost", computeUnitTotalCost),
        ("Manpower", "%(manpower)d"),
        ("Train time", "%(training_time)d"),
        ("Supply", "%(supply_consumption)0.2f"),
        ("Weight", "%(weight)0.1f"),
        ("Width", "%(combat_width)d"),
        ("Speed", computeUnitStatFunction("maximum_speed", combiner = max, baseValue = 0)),
        ("Org.", "%(max_organisation)d"),
        ("Recovery", "%(default_morale)0.1f"),
        ("HP", "%(max_strength)0.1f"),
        ("Hardness", computeUnitStatFunction("hardness", formatString = "%d", combiner = max, baseValue = 0, displayZero = True, usePercent = True), None),
        ("Soft attack", computeUnitStatFunction("soft_attack")),
        ("Hard attack", computeUnitStatFunction("hard_attack")),
        ("Air attack", computeUnitStatFunction("air_attack")),
        ("Defense", computeUnitStatFunction("defense")),
        ("Breakthru", computeUnitStatFunction("breakthrough")),
        ("Armor", computeUnitStatFunction("armor_value", combiner = max, baseValue = 0)),
        ("Piercing", computeUnitStatFunction("ap_attack")),
        ],
    "naval" : [
        ("IC cost", computeUnitCost),
        ("Resource cost", computeUnitResourceCost),
        ("Total cost", computeUnitTotalCost),
        ("Port usage", computeUnitStatFunction("port_capacity_usage")),
        ("Speed", computeUnitStatFunction("naval_speed")),
        ("Gun range", computeUnitStatFunction("fire_range")),
        ("Gun attack", computeUnitStatFunction("attack")),
        ("Torpedo attack", computeUnitStatFunction("torpedo_attack")),
        ("Anti air attack", computeUnitStatFunction("anti_air_attack")),
        ("Sub attack", computeUnitStatFunction("sub_attack")),
        ("Armor", computeUnitStatFunction("armor_value", combiner = max, baseValue = 0)),
        ("Evasion", computeUnitStatFunction("evasion", combiner = max, baseValue = 0)),
        ("Piercing", computeUnitStatFunction("ap_attack")),
        ],
    "air" : [
        ("IC cost", computeUnitCost),
        ("Resource cost", computeUnitResourceCost),
        ("Total cost", computeUnitTotalCost),
        ("Range", computeUnitStatFunction("air_range")),
        ("Speed", computeUnitStatFunction("maximum_speed")),
        ("Agility", computeUnitStatFunction("air_agility")),
        ("Air attack", computeUnitStatFunction("air_attack")),
        ("Ground attack", computeUnitStatFunction("air_ground_attack")),
        ("Naval attack", computeUnitStatFunction("naval_strike_attack", formatString = "%0.1f")),
        ("Naval targeting", computeUnitStatFunction("naval_strike_targetting", formatString = "%0.1f")),
        ("Bombing", computeUnitStatFunction("air_bombing")),
        ("Air defense", computeUnitStatFunction("air_defence")),
        ]
    }

equipmentColumns = {
    "land" : (
        ("Equipment", equipmentName),
        ("Year", "%(year)d"),
        ("IC cost", computeEquipmentCost),
        ("Resource cost", computeEquipmentResourceCost),
        ("Total cost", computeEquipmentTotalCost),
        ("Soft attack", "%(soft_attack)d"),
        ("Hard attack", "%(hard_attack)d"),
        ("Air attack", "%(air_attack)d"),
        ("Defense", "%(defense)d"),
        ("Breakthrough", "%(breakthrough)d"),
        ("Armor", "%(armor_value)d"),
        ("Piercing", "%(ap_attack)d"),
        ),
    "naval" : (
        ("Equipment", equipmentName),
        ("Year", "%(year)d"),
        ("IC cost", computeEquipmentCost),
        ("Resource cost", computeEquipmentResourceCost),
        ("Total cost", computeEquipmentTotalCost),
        ("Manpower", "%(manpower)d"),
        
        ("Port usage", "%(port_capacity_usage)0.1f"),
        ("Operational range", "%(naval_range)d"),
        ("Speed", "%(naval_speed)d"),
        
        ("Surface detection", "%(surface_detection)d"),
        ("Sub detection", "%(sub_detection)d"),
        ("Surface visibility", "%(surface_visibility)d"),
        ("Submerged visibility", "%(sub_visibility)d"),
        
        ("HP", computeNavalMaxStrength),
        ("Evasion", "%(evasion)d"),
        ("Reliability", lambda k, v: "%d%%" % (v['reliability'] * 100.0)),
        
        ("Gun range", "%(fire_range)d"),
        ("Gun attack", "%(attack)d"),
        ("Torpedo attack", "%(torpedo_attack)d"),
        ("Anti air attack", "%(anti_air_attack)d"),
        ("Sub attack", "%(sub_attack)d"),
        ("Shore bombardment", "%(shore_bombardment)d"),
        
        ("Armor", "%(armor_value)d"),
        ("Piercing", "%(ap_attack)d"),
        
        ("Deck size", "%(carrier_size)d"),
        
        ("Equipment", equipmentName),
        ),
    "air" : (
        ("Equipment", equipmentName),
        ("Year", "%(year)d"),
        ("IC cost", computeEquipmentCost),
        ("Resource cost", computeEquipmentResourceCost),
        ("Total cost", computeEquipmentTotalCost),
        ("Manpower", "%(manpower)d"),
        ("Range", "%(air_range)d"),
        ("Speed", "%(maximum_speed)d"),
        ("Agility", "%(air_agility)d"),
        ("Air attack", "%(air_attack)d"),
        ("Ground attack", "%(air_ground_attack)d"),
        ("Naval attack", "%(naval_strike_attack)0.1f"),
        ("Naval targeting", "%(naval_strike_targetting)0.1f"),
        ("Bombing", "%(air_bombing)d"),
        ("Air defense", "%(air_defence)d"),
        )
    }
