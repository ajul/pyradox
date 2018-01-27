import _initpath
import os
import load.tech
import load.unit

import pyradox
import pyradox


from unitstats import compute_unit_type, compute_unit_name

units = load.unit.get_units()["sub_units"]

terrains = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'terrain', '00_terrain.txt'), verbose=False)['categories']

land_terrain_keys = [key for key, value in terrains.items() if "movement_cost" in value and not value["is_water"]]

def compute_is_support(unit):
    return unit["group"] == "support"

def compute_unit_terrain_stat(unit, terrain_key, stat_key):
    if terrain_key in unit:
        return unit[terrain_key][stat_key] or 0.0
    return 0.0

def colored_percent_string(x):
    if x > 0.0:
        return "{{green|%+d%%}}" % round(x * 100.0)
    elif x < 0.0:
        return "{{red|%+d%%}}" % round(x * 100.0)
    else:
        return ""

def compute_unit_stat_function(terrain_key, stat_key):
    if terrain_key in terrains and "units" in terrains[terrain_key]:
        base_modifier = terrains[terrain_key]["units"][stat_key] or 0.0
    else:
        base_modifier = 0.0
    def result_function(unit_key, unit):
        result = compute_unit_terrain_stat(unit, terrain_key, stat_key)
        return colored_percent_string(result)
    return result_function

def compute_small_river_stat_function(stat_key):
    if stat_key == "attack": base_modifier = -0.3
    elif stat_key == "movement": base_modifier = -0.25
    else: base_modifier = 0.0
    def result_function(unit_key, unit):
        result = compute_unit_terrain_stat(unit, "river", stat_key)
        # if stat_key != "defence": result = min(result, 0)
        return colored_percent_string(result)
    return result_function

def compute_large_river_stat_function(stat_key):
    if stat_key == "attack": base_modifier = -0.6
    elif stat_key == "movement": base_modifier = -0.5
    else: base_modifier = 0.0
    def result_function(unit_key, unit):
        result = compute_unit_terrain_stat(unit, "river", stat_key)
        # if stat_key != "defence": result = min(result, 0)
        return colored_percent_string(result)
    return result_function

def compute_amphibious_stat_function(stat_key):
    if stat_key == "attack": base_modifier = -0.7
    else: base_modifier = 0.0
    def result_function(unit_key, unit):
        result = compute_unit_terrain_stat(unit, "amphibious", stat_key)
        # if stat_key != "defence": result = min(result, 0)
        return colored_percent_string(result)
    return result_function

def make_columns(stat_key, include_last = True):
    result = (
        [("Unit", compute_unit_name),
         ("Type", lambda k, v: "Support" if compute_is_support(v) else "Combat"),
         ] +
        [(terrain_key.title(), compute_unit_stat_function(terrain_key, stat_key), None) for terrain_key in land_terrain_keys] +
        [
            ("Small river", compute_small_river_stat_function(stat_key), None),
            ("Large river", compute_large_river_stat_function(stat_key), None)])
    if include_last:
        result += [
            ("Amphibious", compute_amphibious_stat_function(stat_key), None),
            ("Fort", compute_unit_stat_function("fort", stat_key), None)]
    return result

file = open("out/unit_terrain.txt", "w")

file.write("=== Attack ===\n")
file.write(pyradox.wiki.make_wikitable(units, make_columns("attack"),
                                      filter_function = lambda k, v: compute_unit_type(v) == "land",
                                      sort_function = lambda key, value: compute_unit_name(key)))
file.write("=== Defense ===\n")
file.write(pyradox.wiki.make_wikitable(units, make_columns("defence"),
                                      filter_function = lambda k, v: compute_unit_type(v) == "land",
                                      sort_function = lambda key, value: compute_unit_name(key)))
file.write("=== Movement ===\n")
file.write(pyradox.wiki.make_wikitable(units, make_columns("movement"),
                                      filter_function = lambda k, v: compute_unit_type(v) == "land",
                                      sort_function = lambda key, value: compute_unit_name(key)))

file.close()
