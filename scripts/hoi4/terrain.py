import hoi4
import os


import pyradox
import pyradox


terrains = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'terrain', '00_terrain.txt'), verbose=False)['categories']

def compute_unit_stat_function(stat_key):
    def compute_unit_stat(terrain_key, terrain):
        if "units" not in terrain: return ""
        return pyradox.wiki.colored_percent_string(terrain["units"][stat_key] or 0.0)

    return compute_unit_stat

columns = (
    ("Terrain", lambda k, v: "[[File:terrain %s.png]] %s" % (k, k.title())),
    ("Movement cost", "%(movement_cost)0.2f"),
    ("Attrition", lambda k, v: pyradox.wiki.colored_percent_string(v["attrition"] or 0.0, color = "red")),
    #("Combat width", lambda k, v: pyradox.format.colored_percent_string(v["combat_width"] or 0.0)),
    ("Attack", compute_unit_stat_function("attack")),
    ("Enemy air superiority", lambda k, v: pyradox.wiki.colored_percent_string(v["enemy_army_bonus_air_superiority_factor"] or 0.0)),
    )

file = open("out/terrain.txt", "w")

file.write(pyradox.wiki.make_wikitable(terrains, columns, lambda k, v: "sound_type" in v and not v["is_water"]))

file.close()
