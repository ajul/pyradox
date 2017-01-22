import _initpath
import os
import pyradox.config
import pyradox.format
import pyradox.struct
import pyradox.txt
import pyradox.wiki

terrains = pyradox.txt.parseFile(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'terrain', '00_terrain.txt'), verbose=False)['categories']

def computeUnitStatFunction(statKey):
    def computeUnitStat(terrainKey, terrain):
        if "units" not in terrain: return ""
        return pyradox.wiki.coloredPercentString(terrain["units"][statKey] or 0.0)

    return computeUnitStat

columns = (
    ("Terrain", lambda k, v: "[[File:terrain %s.png]] %s" % (k, k.title())),
    ("Movement cost", "%(movement_cost)0.2f"),
    ("Attrition", lambda k, v: pyradox.wiki.coloredPercentString(v["attrition"] or 0.0, color = "red")),
    #("Combat width", lambda k, v: pyradox.format.coloredPercentString(v["combat_width"] or 0.0)),
    ("Attack", computeUnitStatFunction("attack")),
    ("Enemy air superiority", lambda k, v: pyradox.wiki.coloredPercentString(v["enemy_army_bonus_air_superiority_factor"] or 0.0)),
    )

file = open("out/terrain.txt", "w")

file.write(pyradox.wiki.makeWikitable(terrains, columns, lambda k, v: "sound_type" in v and not v["is_water"]))

file.close()
