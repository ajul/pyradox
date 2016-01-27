import _initpath
import pyradox.hoi3.tech
import pyradox.hoi3.unit

techs = pyradox.hoi3.tech.getTechs()

def unitsAtYear(year):
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
        unitData["year"] = year
        unitData["build_cost_ic"] *= multiplier
        unitData["build_time"] *= multiplier
        unitData["supply_consumption"] *= multiplier
        unitData["fuel_consumption"] *= multiplier
    return units

baseColumns = {
    "land" : (
        ("Unit", None),
        ("IC", "%(build_cost_ic).3f"),
        ("Time", "%(build_time)d"),
        ("MP", "%(build_cost_manpower).2f"),
        ("Officers", "%(officers)d"),
        ("Str", "%(max_strength)d"),
        ("Org", "%(default_organisation)d"),
        ("Morale", "%(default_morale).2f"),
        ("Width", "%(combat_width).1f"),
        
        ("Soft Att.", "%(soft_attack).2f"),
        ("Hard Att.", "%(hard_attack).2f"),
        ("Air Att.", "%(air_attack).2f"),
        ("Pierce", "%(ap_attack).1f"),
        
        ("Def.", "%(defensiveness).2f"),
        ("Tough.", "%(toughness).2f"),
        ("Air Def.", "%(air_defence).2f"),
        ("Armor", "%(armor_value).1f"),
        ("Softness", "%(softness).2f"),
        
        ("Speed", "%(maximum_speed).2f"),
        ("Suppression", "%(suppression).2f"),
        ("Supply Cons.", "%(supply_consumption).3f"),
        ("Fuel Cons.", "%(fuel_consumption).3f"),
        ),
    "naval" : (
        ("Unit", None),
        ("IC", "%(build_cost_ic).3f"),
        ("Time", "%(build_time)d"),
        ("MP", "%(build_cost_manpower).2f"),
        ("Hull", "%(hull).2f"),
        ("Org", "%(default_organisation)d"),
        ("Morale", "%(default_morale).2f"),
        
        ("Sea Att.", "%(sea_attack).2f"),
        ("Air Att.", "%(air_attack).2f"),
        ("Convoy Att.", "%(convoy_attack).2f"),
        ("Sub Att.", "%(sub_attack).2f"),
        ("Shore Bomb.", "%(shore_bombardment).2f"),
        ("Fire Dist.", "%(distance).2f"),

        ("Sea Def.", "%(sea_defence).2f"),
        ("Air Def.", "%(air_defence).2f"),

        ("Visibility", "%(visibility)d"),
        ("Surface Det.", "%(surface_detection).2f"),
        ("Air Det.", "%(air_detection).2f"),
        ("Sub Det.", "%(sub_detection).2f"),
        
        ("Speed", "%(maximum_speed).2f"),
        ("Range", "%(range).2f"),
        ("Supply Cons.", "%(supply_consumption).3f"),
        ("Fuel Cons.", "%(fuel_consumption).3f"),
        ),
    "air" : (
        ("Unit", None),
        ("IC", "%(build_cost_ic).3f"),
        ("Time", "%(build_time)d"),
        ("MP", "%(build_cost_manpower).2f"),
        ("Org", "%(default_organisation)d"),
        ("Morale", "%(default_morale).2f"),

        ("Soft Att.", "%(soft_attack).2f"),
        ("Hard Att.", "%(hard_attack).2f"),
        ("Strat Att.", "%(strategic_attack).2f"),
        ("Sea Att.", "%(sea_attack).2f"),
        ("Air Att.", "%(air_attack).2f"),
        ("Sub Att.", "%(sub_attack).2f"),

        ("Surface Def.", "%(surface_defence).2f"),
        ("Air Def.", "%(air_defence).2f"),

        ("Surface Det.", "%(surface_detection).2f"),
        ("Air Det.", "%(air_detection).2f"),

        ("Speed", "%(maximum_speed)d"),
        ("Range", "%(range)d"),
        ("Supply Cons.", "%(supply_consumption).3f"),
        ("Fuel Cons.", "%(fuel_consumption).3f"),
        )
    }

derivedColumns = {
    "land" : (
        ("Year", "%(year)d"),
        ("kICd", lambda k, v: '%0.3f' % (0.001 * v["build_cost_ic"] * v["build_time"])),
        ("Soft Att./kICd", lambda k, v: '%0.3f' % (1000 * v["soft_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Soft Att./MP", lambda k, v: '%0.3f' % (v["soft_attack"] / v["build_cost_manpower"])),
        ("Soft Att./Cons.", lambda k, v: '%0.3f' % (v["soft_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),
        
        ("Hard Att./kICd", lambda k, v: '%0.3f' % (1000 * v["hard_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Hard Att./MP", lambda k, v: '%0.3f' % (v["hard_attack"] / v["build_cost_manpower"])),
        ("Hard Att./Cons.", lambda k, v: '%0.3f' % (v["hard_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),
        ),
    "naval" : (
        ("Year", "%(year)d"),
        ("kICd", lambda k, v: '%0.3f' % (0.001 * v["build_cost_ic"] * v["build_time"])),
        
        ("Sea Att./kICd", lambda k, v: '%0.3f' % (1000 * v["sea_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Sea Att./MP", lambda k, v: '%0.3f' % (v["sea_attack"] / v["build_cost_manpower"])),
        ("Sea Att./Cons.", lambda k, v: '%0.3f' % (v["sea_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),

        ("Air Att./kICd", lambda k, v: '%0.3f' % (1000 * v["air_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Air Att./MP", lambda k, v: '%0.3f' % (v["air_attack"] / v["build_cost_manpower"])),
        ("Air Att./Cons.", lambda k, v: '%0.3f' % (v["air_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),

        ("Sub Att./kICd", lambda k, v: '%0.3f' % (1000 * v["sub_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Sub Att./MP", lambda k, v: '%0.3f' % (v["sub_attack"] / v["build_cost_manpower"])),
        ("Sub Att./Cons.", lambda k, v: '%0.3f' % (v["sub_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),
        ),
    "air" : (
        ("Year", "%(year)d"),
        ("kICd", lambda k, v: '%0.3f' % (0.001 * v["build_cost_ic"] * v["build_time"])),
        ("Soft Att./kICd", lambda k, v: '%0.3f' % (1000 * v["soft_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Soft Att./MP", lambda k, v: '%0.3f' % (v["soft_attack"] / v["build_cost_manpower"])),
        ("Soft Att./Cons.", lambda k, v: '%0.3f' % (v["soft_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),
        
        ("Hard Att./kICd", lambda k, v: '%0.3f' % (1000 * v["hard_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Hard Att./MP", lambda k, v: '%0.3f' % (v["hard_attack"] / v["build_cost_manpower"])),
        ("Hard Att./Cons.", lambda k, v: '%0.3f' % (v["hard_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),

        ("Strat. Att./kICd", lambda k, v: '%0.3f' % (1000 * v["strategic_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Strat. Att./MP", lambda k, v: '%0.3f' % (v["strategic_attack"] / v["build_cost_manpower"])),
        ("Strat. Att./Cons.", lambda k, v: '%0.3f' % (v["strategic_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),
        
        ("Air Att./kICd", lambda k, v: '%0.3f' % (1000 * v["air_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Air Att./MP", lambda k, v: '%0.3f' % (v["air_attack"] / v["build_cost_manpower"])),
        ("Air Att./Cons.", lambda k, v: '%0.3f' % (v["air_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),
        
        ("Sea Att./kICd", lambda k, v: '%0.3f' % (1000 * v["sea_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Sea Att./MP", lambda k, v: '%0.3f' % (v["sea_attack"] / v["build_cost_manpower"])),
        ("Sea Att./Cons.", lambda k, v: '%0.3f' % (v["sea_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),

        ("Sub Att./kICd", lambda k, v: '%0.3f' % (1000 * v["sub_attack"] / (v["build_cost_ic"] * v["build_time"]))),
        ("Sub Att./MP", lambda k, v: '%0.3f' % (v["sub_attack"] / v["build_cost_manpower"])),
        ("Sub Att./Cons.", lambda k, v: '%0.3f' % (v["sub_attack"] / (v["supply_consumption"] + v["fuel_consumption"]))),
        ),
    }
