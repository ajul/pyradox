import _initpath
import pyradox.hoi3.tech
import pyradox.hoi3.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki

columns = {
    "land" : (
        ("Unit", None),
        ("IC", "build_cost_ic"),
        ("Time", "build_time"),
        ("Manpower", "build_cost_manpower"),
        ("Officers", "officers"),
        ("Str", "max_strength"),
        ("Org", "default_organisation"),
        ("Width", "combat_width"),
        ("Soft Attack", "soft_attack"),
        ("Hard Attack", "hard_attack"),
        ("Piercing Attack", "ap_attack"),
        ("Armor", "armor_value"),
        ("Air Attack", "air_attack"),
        ("Defensiveness", "defensiveness"),
        ("Toughness", "toughness"),
        ("Air Defense", "air_defence"),
        ("Softness", "softness"),
        ("Speed", "maximum_speed"),
        ("Suppression", "suppression"),
        ("Supply Consumption", "supply_consumption"),
        ("Fuel Consumption", "fuel_consumption"),
        ),
    "naval" : (

        ),
    "air" : (
        
        )
    }

techs = pyradox.hoi3.tech.getTechs()

f = open("out/land_units.txt", "w")
for year in range(1936, 1949):
    units = pyradox.hoi3.unit.getUnits()
    
    for unitKey, unitData in units.items():
        if "active" not in unitData.keys(): unitData["active"] = True
        unitData["num_upgrades"] = 0
    
    for tech in techs.values():
        level = pyradox.hoi3.tech.getTechLevel(tech, year)
        if level == 0: continue
        
        for unitKey, effects in tech.items():
            if unitKey == "activate_unit" and effects in units.keys():
                units[effects]["active"] = True # activate unit
            if unitKey not in units.keys(): continue

            unitData = units[unitKey]
            unitData["num_upgrades"] += level
            
            for effect, amount in effects.items():
                if effect not in unitData: continue
                if isinstance(amount, pyradox.struct.Tree): continue
                unitData[effect] += level * amount

    for unitKey, unitData in units.items():
        multiplier = 1.00 + unitData["num_upgrades"] * 0.01
        unitData["build_cost_ic"] *= multiplier
        unitData["build_time"] *= multiplier
        unitData["supply_consumption"] *= multiplier
        unitData["fuel_consumption"] *= multiplier
    
    f.write("== %d ==\n" % year)
    f.write(pyradox.wiki.makeWikitable(units, columns["land"], lambda k, v: v["type"] == "land" and v["active"]))

f.close()
