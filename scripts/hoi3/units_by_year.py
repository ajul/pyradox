import _initpath
import pyradox.hoi3.tech
import pyradox.hoi3.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki

columns = {
    "land" : (
        ("Unit", None),
        ("IC", "%(build_cost_ic).3f"),
        ("Time", "%(build_time)d"),
        ("Manpower", "%(build_cost_manpower).2f"),
        ("Officers", "%(officers)d"),
        ("Str", "%(max_strength)d"),
        ("Org", "%(default_organisation)d"),
        ("Morale", "%(default_morale).2f"),
        ("Width", "%(combat_width).1f"),
        
        ("Soft Attack", "%(soft_attack).2f"),
        ("Hard Attack", "%(hard_attack).2f"),
        ("Piercing Attack", "%(ap_attack).1f"),
        ("Air Attack", "%(air_attack).2f"),
        
        ("Defensiveness", "%(defensiveness).2f"),
        ("Toughness", "%(toughness).2f"),
        ("Armor", "%(armor_value).1f"),
        ("Air Defense", "%(air_defence).2f"),
        ("Softness", "%(softness).2f"),
        
        ("Speed", "%(maximum_speed).2f"),
        ("Suppression", "%(suppression).2f"),
        ("Supply Consumption", "%(supply_consumption).3f"),
        ("Fuel Consumption", "%(fuel_consumption).3f"),
        ),
    "naval" : (
        ("Unit", None),
        ("IC", "%(build_cost_ic).3f"),
        ("Time", "%(build_time)d"),
        ("Manpower", "%(build_cost_manpower).2f"),
        ("Hull", "%(hull).2f"),
        ("Org", "%(default_organisation)d"),
        ("Morale", "%(default_morale).2f"),
        
        ("Sea Attack", "%(sea_attack).2f"),
        ("Air Attack", "%(air_attack).2f"),
        ("Convoy Attack", "%(convoy_attack).2f"),
        ("Sub Attack", "%(sub_attack).2f"),
        ("Shore Bombardment", "%(shore_bombardment).2f"),
        ("Firing Distance", "%(distance).2f"),

        ("Sea Defense", "%(sea_defence).2f"),
        ("Air Defense", "%(air_defence).2f"),

        ("Visibility", "%(visibility)d"),
        ("Surface Detection", "%(surface_detection).2f"),
        ("Air Detection", "%(air_detection).2f"),
        ("Sub Detection", "%(sub_detection).2f"),
        
        ("Speed", "%(maximum_speed).2f"),
        ("Range", "%(range).2f"),
        ("Supply Consumption", "%(supply_consumption).3f"),
        ("Fuel Consumption", "%(fuel_consumption).3f"),
        ),
    "air" : (
        ("Unit", None),
        ("IC", "%(build_cost_ic).3f"),
        ("Time", "%(build_time)d"),
        ("Manpower", "%(build_cost_manpower).2f"),
        ("Org", "%(default_organisation)d"),
        ("Morale", "%(default_morale).2f"),

        ("Soft Attack", "%(soft_attack).2f"),
        ("Hard Attack", "%(hard_attack).2f"),
        ("Strategic Attack", "%(strategic_attack).2f"),
        ("Sea Attack", "%(sea_attack).2f"),
        ("Air Attack", "%(air_attack).2f"),
        ("Sub Attack", "%(sub_attack).2f"),

        ("Surface Defense", "%(surface_defence).2f"),
        ("Air Defense", "%(air_defence).2f"),

        ("Surface Detection", "%(surface_detection).2f"),
        ("Air Detection", "%(air_detection).2f"),

        ("Speed", "%(maximum_speed).2f"),
        ("Range", "%(range).2f"),
        ("Supply Consumption", "%(supply_consumption).3f"),
        ("Fuel Consumption", "%(fuel_consumption).3f"),
        )
    }

techs = pyradox.hoi3.tech.getTechs()

files = {}
for unitType in columns.keys():
    files[unitType] = open("out/%s_units.txt" % unitType, "w")

for year in range(1936, 1948):
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

    for unitType, unitFile in files.items():
        unitFile.write("== %d ==\n" % year)
        unitFile.write(pyradox.wiki.makeWikitable(units, columns[unitType], lambda k, v: v["type"] == unitType and v["active"]))

for unitFile in files.values():
    unitFile.close()
