import copy
import pyradox

default_year = 1918
module_year_fallback = {
    'ship_anti_air_1' : default_year,
    'ship_fire_control_system_1' : 1937,
    'ship_fire_control_system_2' : 1939,
    'ship_fire_control_system_3' : 1941,
}

def get_modules(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    technologies = pyradox.parse_merge('common/technologies', game = game, merge_levels = 1)['technologies']
    modules = pyradox.parse_merge('common/units/equipment/modules', game = game, merge_levels = 1)['equipment_modules']
    
    for key, technology in technologies.items():
        if not isinstance(technology, pyradox.Tree): continue
        start_year = technology['start_year']
        for module_key in technology.find_all('enable_equipment_modules'):
            if module_key in modules:
                # print(module_key, start_year)
                if start_year is None:
                    start_year = module_year_fallback[module_key]
                modules[module_key]['start_year'] = start_year
    
    for module_key, module in modules.items():
        if module['start_year'] is None: 
            print('No tech found for ' + module_key + '; setting default year of ' + str(default_year))
            module['start_year'] = default_year
    
    return modules

def get_hulls(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    
    equipments = pyradox.parse_merge('common/units/equipment', game = game, filter_pattern = "ship_hull", merge_levels = 1)['equipments']
    
    archetypes = pyradox.Tree()
    # Compute archetypes.
    for key, hull in equipments.items():
        if hull['is_archetype']:
            hull = copy.deepcopy(hull)
            hull['module_slots'].resolve_references()
            archetypes[key] = hull
    
    hulls = pyradox.Tree()
    # Compute final hulls.
    for key, hull in equipments.items():
        if hull['is_buildable'] is False: continue
        
        hull = copy.deepcopy(hull)
        
        archetype = archetypes[hull['archetype']]
        hull.inherit(archetype)
        hull.weak_update(archetype)
        
        if 'parent' in hull:
            parent = hulls[hull['parent']]
            hull.inherit(parent)
        
        hull['module_slots'].resolve_references()
        hull['is_archetype'] = False
        hull['is_buildable'] = True
        
        hulls[key] = hull
    
    return archetypes, hulls

def make_ship(hull, design):
    ship = copy.deepcopy(hull)

    ship['design_modules'] = pyradox.Tree()

    for slot_key, module_key, module in design:
        ship['design_modules'].append(slot_key, module_key)

    # resource costs
    for slot_key, module_key,module in design:
        if 'build_cost_resources' in module:
            for resource, amount in module['build_cost_resources'].items():
                ship['resources'][resource] = (
                    (ship['resources'][resource] or 0)
                    + amount)

    ship['total_resources'] = sum(ship['resources'].values())

    # add_stats
    for slot_key, module_key, module in design:
        if 'add_stats' in module:
            for stat, amount in module['add_stats'].items():
                ship[stat] = (ship[stat] or 0) + amount

    # average stats
    average_dict = {}

    for slot_key, module_key, module in design:
        if 'add_average_stats' in module:
            for stat, amount in module['add_average_stats'].items():
                if stat in average_dict:
                    prev_total, prev_count = average_dict[stat]
                else:
                    prev_total, prev_count = 0.0, 0
                average_dict[stat] = (prev_total + amount, prev_count + 1)

    for stat, (total, count) in average_dict.items():
        ship[stat] = (ship[stat] or 0) + total / count
    
    # multiply stats
    multiply_dict = {}

    for slot_key, module_key, module in design:
        if 'multiply_stats' in module:
            for stat, amount in module['multiply_stats'].items():
                if stat not in multiply_dict: multiply_dict[stat] = 0.0
                multiply_dict[stat] += amount

    for stat, amount in multiply_dict.items():
        ship[stat] *= (1.0 + amount)

    return ship
