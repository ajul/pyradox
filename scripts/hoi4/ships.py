import copy
import hoi4
import hoi4.ship
import pyradox

archetypes, hulls = hoi4.ship.get_hulls()
modules = hoi4.ship.get_modules()

negative_stats = [
    'build_cost_ic',
    'fuel_consumption',
    'sub_visibility',
    'surface_visibility',
]

strategies = {
    'heavy_then_light' : [
        'hg_attack',
        'lg_attack',
        'armor_value',
        'anti_air_attack',
        'surface_detection',
        'sub_detection',
        'sub_attack',
        'carrier_size',
        'torpedo_attack',
        'naval_speed',
        'naval_range',
    ],
    'heavy_then_aa' : [
        'hg_attack',
        'anti_air_attack',
        'armor_value',
        'lg_attack',
        'surface_detection',
        'sub_detection',
        'sub_attack',
        'carrier_size',
        'torpedo_attack',
        'naval_speed',
        'naval_range',
    ],
    'light_then_aa' : [
        'lg_attack',
        'anti_air_attack',
        'armor_value',
        'hg_attack',
        'surface_detection',
        'sub_detection',
        'sub_attack',
        'carrier_size',
        'torpedo_attack',
        'naval_speed',
        'naval_range',
    ],
    'aa' : [
        'anti_air_attack',
        'lg_attack',
        'armor_value',
        'surface_detection',
        'torpedo_attack',
        'hg_attack',
        'sub_detection',
        'sub_attack',
        'carrier_size',
        'naval_speed',
        'naval_range',
    ],
    'torpedo' : [
        'torpedo_attack',
        'sub_visibility',
        'lg_attack',
        'hg_attack',
        'armor_value',
        'anti_air_attack',
        'surface_detection',
        'sub_detection',
        'sub_attack',
        'carrier_size',
        'naval_speed',
        'naval_range',
    ],
    'carrier_fast' : [
        'carrier_size',
        'naval_speed',
        'anti_air_attack',
        'surface_detection',
        'sub_detection',
        'naval_range',
    ],
}

# selects modules, ranking by stats in order of strategy
# with add > average > mult
def select_modules(hull, strategy, year = None):
    if year is None: year = hull['year']
    design = []

    for slot_key, slot in hull['module_slots'].items():
        selected_key = None
        selected_module = None
        if slot['required'] is True:
            selected_score = [] # empty list is less than all other lists
        else:
            selected_score = [(0, 0, 0)] * len(strategy)
        for module_key, module in modules.items():
            if module['category'] not in slot.find_all('allowed_module_categories'): continue
            if module['start_year'] > year: continue
            score = []
            for stat in strategy:
                # special case
                if stat == 'total_resources':
                    if 'build_cost_resources' in module:
                        score.append(-sum(module['build_cost_resources'].values()))
                    else:
                        score.append(0)
                    continue
                add = 0
                average = 0
                multiply = 0.0
                if 'add_stats' in module: add = module['add_stats'][stat] or 0
                if 'add_average_stats' in module: average = module['add_average_stats'][stat] or 0
                if 'multiply_stats' in module: multiply = module['multiply_stats'][stat] or 0.0
                if stat in negative_stats:
                    add, average, multiply = -add, -average, -multiply
                score.append((add, average, multiply))
            # print(module_key, score)    
            if score > selected_score:
                selected_key = module_key
                selected_module = module
                selected_score = score
        if selected_module is not None:
            # print('Selected ' + selected_key + ' for ' + slot_key)
            design.append((slot_key, selected_key, selected_module))
    return design

def design_ship(hull, strategy, year = None):
    design = select_modules(hull, strategy, year = year)
    ship = hoi4.ship.make_ship(hull, design)
    return ship

model_specs = [
    ('ship_hull_light_1', 'aa', 1932),
    ('ship_hull_light_2', 'aa', 1936),
    ('ship_hull_light_3', 'aa', 1940),
    ('ship_hull_light_4', 'aa', 1944),
    
    ('ship_hull_light_1', 'torpedo', 1932),
    ('ship_hull_light_2', 'torpedo', 1936),
    ('ship_hull_light_3', 'torpedo', 1940),
    ('ship_hull_light_4', 'torpedo', 1944),

    ('ship_hull_light_1', 'light_then_aa', 1932),
    ('ship_hull_light_2', 'light_then_aa', 1936),
    ('ship_hull_light_3', 'light_then_aa', 1940),
    ('ship_hull_light_4', 'light_then_aa', 1944),
    
    ('ship_hull_cruiser_1', 'aa', 1932),
    ('ship_hull_cruiser_2', 'aa', 1936),
    ('ship_hull_cruiser_3', 'aa', 1940),
    ('ship_hull_cruiser_4', 'aa', 1944),

    ('ship_hull_cruiser_1', 'torpedo', 1932),
    ('ship_hull_cruiser_2', 'torpedo', 1936),
    ('ship_hull_cruiser_3', 'torpedo', 1940),
    ('ship_hull_cruiser_4', 'torpedo', 1944),

    ('ship_hull_torpedo_cruiser', 'torpedo', 1940),
    
    ('ship_hull_cruiser_1', 'light_then_aa', 1932),
    ('ship_hull_cruiser_2', 'light_then_aa', 1936),
    ('ship_hull_cruiser_3', 'light_then_aa', 1940),
    ('ship_hull_cruiser_4', 'light_then_aa', 1944),

    ('ship_hull_cruiser_1', 'heavy_then_aa', 1932),
    ('ship_hull_cruiser_2', 'heavy_then_aa', 1936),
    ('ship_hull_cruiser_3', 'heavy_then_aa', 1940),
    ('ship_hull_cruiser_4', 'heavy_then_aa', 1944),
    
    ('ship_hull_cruiser_1', 'heavy_then_light', 1932),
    ('ship_hull_cruiser_2', 'heavy_then_light', 1936),
    ('ship_hull_cruiser_3', 'heavy_then_light', 1940),
    ('ship_hull_cruiser_4', 'heavy_then_light', 1944),

    ('ship_hull_cruiser_panzerschiff', 'heavy_then_light', 1936),
    ('ship_hull_cruiser_coastal_defense_ship', 'heavy_then_light', 1936),

    ('ship_hull_heavy_1', 'aa', 1932),
    ('ship_hull_heavy_2', 'aa', 1936),
    ('ship_hull_heavy_3', 'aa', 1940),
    ('ship_hull_heavy_4', 'aa', 1944),

    ('ship_hull_heavy_1', 'heavy_then_aa', 1932),
    ('ship_hull_heavy_2', 'heavy_then_aa', 1936),
    ('ship_hull_heavy_3', 'heavy_then_aa', 1940),
    ('ship_hull_heavy_3', 'heavy_then_aa', 1944),
    ('ship_hull_heavy_4', 'heavy_then_aa', 1944),
    
    ('ship_hull_heavy_1', 'heavy_then_light', 1932),
    ('ship_hull_heavy_2', 'heavy_then_light', 1936),
    ('ship_hull_heavy_3', 'heavy_then_light', 1940),
    ('ship_hull_heavy_4', 'heavy_then_light', 1944),

    ('ship_hull_pre_dreadnought', 'heavy_then_light', 1932),

    ('ship_hull_super_heavy_1', 'heavy_then_light', 1940),
    ('ship_hull_super_heavy_1', 'heavy_then_light', 1944),

    ('ship_hull_submarine_1', 'torpedo', 1932),
    ('ship_hull_submarine_2', 'torpedo', 1936),
    ('ship_hull_submarine_3', 'torpedo', 1940),
    ('ship_hull_submarine_4', 'torpedo', 1944),

    ('ship_hull_cruiser_submarine', 'torpedo', 1940),

    ('ship_hull_carrier_1', 'carrier_fast', 1936),
    ('ship_hull_carrier_2', 'carrier_fast', 1940),
    ('ship_hull_carrier_3', 'carrier_fast', 1944),

    ('ship_hull_carrier_conversion_ca', 'carrier_fast', 1936),
    ('ship_hull_carrier_conversion_bb', 'carrier_fast', 1936),
]

models = pyradox.Tree()
for hull_key, strategy_key, year in model_specs:
    hull = hulls[hull_key]
    strategy = strategies[strategy_key]
    ship = design_ship(hull, strategy, year = year)

    ship['model_year'] = year
    
    model_key = '%s, %s, %d' % (hull_key, strategy_key, year)
    ship['model_id'] = model_key
    models[model_key] = ship

print('List of hulls:')
for hull_key in hulls:
    if 'hull' in hull_key: print(hull_key)

print('Example model:')
print(models.at(0)[1])

columns = [
    ('Model', '%(model_id)s'),
    ('Prod', '%(build_cost_ic)d'),
    ('Res/IC', '%(total_resources)d'),
    ('Res-prod', lambda k, v: '%d' % (v['build_cost_ic'] * v['total_resources'])),
    ('Total prod eq.', lambda k, v: '%d' % (v['build_cost_ic'] * (1.0 + v['total_resources'] * 108 / 64 / 8))),
    ('Manpower', '%(manpower)d'),

    ('HP', '%(max_strength)0.1f'),
    ('Armor', '%(armor_value)0.1f'),
    ('Speed', '%(naval_speed)0.1f'),
    ('Reliability', '%(reliability)0.2f'),
    ('Fuel', '%(fuel_consumption)0.1f'),
    ('Surf visibility', '%(surface_visibility)0.1f'),
    ('Sub visibility', '%(sub_visibility)0.1f'),

    ('LG Attack', '%(lg_attack)0.1f'),
    ('LG Piercing', '%(lg_armor_piercing)0.1f'),
    ('HG Attack', '%(hg_attack)0.1f'),
    ('HG Piercing', '%(hg_armor_piercing)0.1f'),
    ('Torpedo', '%(torpedo_attack)0.1f'),
    ('AA', '%(anti_air_attack)0.1f'),
    ('Planes', '%(carrier_size)0.1f'),

    ('Modules', lambda k, v: ', '.join(v['design_modules'].values()))
]

pyradox.csv.write_tree(models, 'out/ship_models.csv', columns, 'excel')
