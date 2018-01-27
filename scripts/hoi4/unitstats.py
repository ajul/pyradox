import _initpath
import re
import pyradox
import load.equipment
import load.tech
import load.unit


factories_per_resource = 1.5 / 8.0

default_year = 1918

techs = load.tech.get_techs()["technologies"]
equipments = load.equipment.get_equipments()["equipments"]
units = load.unit.get_units()["sub_units"]

for equipment_key, equipment_value in equipments.items():
    if "archetype" in equipment_value:
        equipment_value.weak_update(equipments[equipment_value["archetype"]])
        equipment_value["is_archetype"] = False
        
for tech_key, tech in techs.items():
    if not isinstance(tech, pyradox.Tree): continue
    year = tech["start_year"] or default_year
    if "enable_equipments" in tech:
        for equipment_key in tech.find_all("enable_equipments"):
            equipment = equipments[equipment_key]
            equipment['year'] = year
    if "enable_subunits" in tech:
        for unit_key in tech.find_all("enable_subunits"):
            units[unit_key]["year"] = year

def units_at_year(year):
    units = load.unit.get_units()["sub_units"]
    
    # archetype_key -> best equipment
    equipment_models = {}
    
    for unit_key, unit_data in units.items():
        unit_data["year"] = year
        unit_data["last_upgrade"] = default_year
        if "active" not in unit_data.keys(): unit_data["active"] = True
    
    for tech_key, tech in techs.items():
        if not isinstance(tech, pyradox.Tree): continue
        if (tech["start_year"] or year) > year: continue
        if tech["allow"] and tech["allow"]["always"] == False: continue # ignore unallowed techs
        if 'folder' in tech and 'doctrine' in tech['folder']['name']: continue # ignore doctrines
        if "enable_equipments" in tech:
            for equipment_key in tech.find_all("enable_equipments"):
                equipment = equipments[equipment_key]
                if "archetype" in equipment:
                    archetype_key = equipment["archetype"]
                    equipment_models[archetype_key] = equipments[equipment_key]
                equipment_models[equipment_key] = equipments[equipment_key]
                # TODO: drop ordering assumption?
        if "enable_subunits" in tech:
            for unit_key in tech.find_all("enable_subunits"):
                units[unit_key]["active"] = True
                units[unit_key]["last_upgrade"] = max(units[unit_key]["last_upgrade"], tech["start_year"])

        # non-equipment modifiers
        for unit_key, unit_data in units.items():
            for tech_unit_key, stats in tech.items():
                if tech_unit_key == unit_key or tech_unit_key in unit_data.find_all('categories'):
                    units[unit_key]["last_upgrade"] = max(units[unit_key]["last_upgrade"], tech["start_year"])
                    for stat_key, stat_value in stats.items():
                        if (not type(stat_value) is pyradox.Tree):
                            unit_data[stat_key] = (unit_data[stat_key] or 0.0) + stat_value

    # fill in equipment
    for unit_key, unit_data in units.items():
        unit_data["equipments"] = pyradox.Tree()
        for archetype_key in unit_data["need"]:
            if archetype_key in equipment_models:
                equipment = equipment_models[archetype_key]
                unit_data["equipments"][archetype_key] = equipment
                unit_data["last_upgrade"] = max(unit_data["last_upgrade"], equipment["year"])
                if not equipments[archetype_key]["is_archetype"]:
                    print("Warning: non-archetype equipment %s defined for %s" % (archetype_key, unit_key))
            else:
                unit_data["equipments"][archetype_key] = False
        
    return units

def compute_unit_name(unit_key, unit = None):
    return pyradox.yml.get_localization(unit_key, ['unit'], game = 'HoI4') or pyradox.format.human_string(unit_key)
    
def compute_unit_type(unit):
    if unit["map_icon_category"] == "ship":
        return "naval"
    elif unit["map_icon_category"] is None:
        return "air"
    else:
        return "land"
        
def compute_equipment_type(equipment):
    if 'air_range' in equipment:
        return 'air'
    elif 'port_capacity_usage' in equipment:
        return 'naval'
    else:
        return 'land'

def is_availiable(unit):
    for equipment_key, equipment in unit["equipments"].items():
        if equipment is False:
            return False
    return unit["active"]

def compute_unit_cost(unit_key, unit_data):
    result = 0
    for archetype_key, quantity in unit_data["need"].items():
        equipment = unit_data["equipments"][archetype_key]
        result += quantity * equipment["build_cost_ic"]
    return "%d" % result

def compute_unit_resource_cost(unit_key, unit_data):
    result = 0
    for archetype_key, quantity in unit_data["need"].items():
        equipment = unit_data["equipments"][archetype_key]
        if "resources" not in equipment: continue
        result += quantity * sum(equipment["resources"].values()) * equipment["build_cost_ic"]
    return "%d" % result

def compute_unit_total_cost(unit_key, unit_data):
    result = 0
    for archetype_key, quantity in unit_data["need"].items():
        equipment = unit_data["equipments"][archetype_key]
        if "resources" not in equipment: continue
        result += quantity * (equipment["build_cost_ic"]
                              + factories_per_resource * sum(equipment["resources"].values()) * equipment["build_cost_ic"])
    return "%d" % result
    
def compute_equipment_cost(equipment_key, equipment):
    return '%d' % equipment['build_cost_ic']
    
def compute_equipment_resource_cost(equipment_key, equipment):
    if "resources" not in equipment: return '0'
    return '%d' % (sum(equipment["resources"].values()) * equipment['build_cost_ic'])
    
def compute_equipment_total_cost(equipment_key, equipment):
    result = equipment['build_cost_ic']
    if "resources" in equipment: result *= (1.0 + factories_per_resource * sum(equipment["resources"].values()))
    return '%d' % result

def compute_unit_stat_function(stat_key, format_string = "%0.1f", combiner = sum, base_value = None, display_zero = False, use_percent = False):
    def result_function(unit_key, unit_data):
        def get_stats():
            if base_value is not None: yield base_value
            for equipment in unit_data["equipments"].values():
                if stat_key in equipment:
                    yield equipment[stat_key]
    
        result = combiner(get_stats()) * (1.0 + (unit_data[stat_key] or 0.0))
        
        if result == 0.0 and not display_zero: return ''
        else: 
            if use_percent:
                return re.sub('%.*?[df]', '\g<0>%%', format_string) % (result * 100.0)
            else:
                return format_string % result

    return result_function
    
def equipment_name(key, value):
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
    
def compute_naval_max_strength(equipment_key, equipment):
    if 'max_strength' in equipment:
        return '%d' % equipment['max_strength']
    for i in range(len(equipment_key)):
        if equipment_key[0:i] in units:
            return '%d' % units[equipment_key[0:i]]['max_strength']

unit_type_years = {
    "land" : [1918, 1934, 1936, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945],
    "naval" : [1922, 1936, 1940, 1944],
    "air" : [1933, 1936, 1940, 1944, 1945, 1950],
}
    
base_columns = {
    "land" : [
        ("Prod. cost", compute_unit_cost),
        ("Res. cost", compute_unit_resource_cost),
        ("Total cost", compute_unit_total_cost),
        ("Manpower", "%(manpower)d"),
        ("Train time", "%(training_time)d"),
        ("Supply", "%(supply_consumption)0.2f"),
        ("Weight", "%(weight)0.1f"),
        ("Width", "%(combat_width)d"),
        ("Speed", compute_unit_stat_function("maximum_speed", combiner = max, base_value = 0)),
        ("Org.", "%(max_organisation)d"),
        ("Recovery", "%(default_morale)0.1f"),
        ("HP", "%(max_strength)0.1f"),
        ("Hardness", compute_unit_stat_function("hardness", format_string = "%d", combiner = max, base_value = 0, display_zero = True, use_percent = True), None),
        ("Soft attack", compute_unit_stat_function("soft_attack")),
        ("Hard attack", compute_unit_stat_function("hard_attack")),
        ("Air attack", compute_unit_stat_function("air_attack")),
        ("Defense", compute_unit_stat_function("defense")),
        ("Breakthru", compute_unit_stat_function("breakthrough")),
        ("Armor", compute_unit_stat_function("armor_value", combiner = max, base_value = 0)),
        ("Piercing", compute_unit_stat_function("ap_attack")),
        ],
    "naval" : [
        ("IC cost", compute_unit_cost),
        ("Resource cost", compute_unit_resource_cost),
        ("Total cost", compute_unit_total_cost),
        ("Port usage", compute_unit_stat_function("port_capacity_usage")),
        ("Speed", compute_unit_stat_function("naval_speed")),
        ("Gun range", compute_unit_stat_function("fire_range")),
        ("Gun attack", compute_unit_stat_function("attack")),
        ("Torpedo attack", compute_unit_stat_function("torpedo_attack")),
        ("Anti air attack", compute_unit_stat_function("anti_air_attack")),
        ("Sub attack", compute_unit_stat_function("sub_attack")),
        ("Armor", compute_unit_stat_function("armor_value", combiner = max, base_value = 0)),
        ("Evasion", compute_unit_stat_function("evasion", combiner = max, base_value = 0)),
        ("Piercing", compute_unit_stat_function("ap_attack")),
        ],
    "air" : [
        ("IC cost", compute_unit_cost),
        ("Resource cost", compute_unit_resource_cost),
        ("Total cost", compute_unit_total_cost),
        ("Range", compute_unit_stat_function("air_range")),
        ("Speed", compute_unit_stat_function("maximum_speed")),
        ("Agility", compute_unit_stat_function("air_agility")),
        ("Air attack", compute_unit_stat_function("air_attack")),
        ("Ground attack", compute_unit_stat_function("air_ground_attack")),
        ("Naval attack", compute_unit_stat_function("naval_strike_attack", format_string = "%0.1f")),
        ("Naval targeting", compute_unit_stat_function("naval_strike_targetting", format_string = "%0.1f")),
        ("Bombing", compute_unit_stat_function("air_bombing")),
        ("Air defense", compute_unit_stat_function("air_defence")),
        ]
    }

equipment_columns = {
    "land" : (
        ("Equipment", equipment_name),
        ("Year", "%(year)d"),
        ("IC cost", compute_equipment_cost),
        ("Resource cost", compute_equipment_resource_cost),
        ("Total cost", compute_equipment_total_cost),
        ("Soft attack", "%(soft_attack)d"),
        ("Hard attack", "%(hard_attack)d"),
        ("Air attack", "%(air_attack)d"),
        ("Defense", "%(defense)d"),
        ("Breakthrough", "%(breakthrough)d"),
        ("Armor", "%(armor_value)d"),
        ("Piercing", "%(ap_attack)d"),
        ),
    "naval" : (
        ("Equipment", equipment_name),
        ("Year", "%(year)d"),
        ("IC cost", compute_equipment_cost),
        ("Resource cost", compute_equipment_resource_cost),
        ("Total cost", compute_equipment_total_cost),
        ("Manpower", "%(manpower)d"),
        
        ("Port usage", "%(port_capacity_usage)0.1f"),
        ("Operational range", "%(naval_range)d"),
        ("Speed", "%(naval_speed)d"),
        
        ("Surface detection", "%(surface_detection)d"),
        ("Sub detection", "%(sub_detection)d"),
        ("Surface visibility", "%(surface_visibility)d"),
        ("Submerged visibility", "%(sub_visibility)d"),
        
        ("HP", compute_naval_max_strength),
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
        
        ("Equipment", equipment_name),
        ),
    "air" : (
        ("Equipment", equipment_name),
        ("Year", "%(year)d"),
        ("IC cost", compute_equipment_cost),
        ("Resource cost", compute_equipment_resource_cost),
        ("Total cost", compute_equipment_total_cost),
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
