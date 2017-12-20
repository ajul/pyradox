import math
import terrain

def province_cost(province_id, province):
    cost = 0
    if 'base_tax' in province:
        cost += province['base_tax'] * 0.5
            
    if 'base_production' in province:
        cost += province['base_production'] * 0.5
        
    if 'base_manpower' in province:
        cost += province['base_manpower'] * 0.5

    if cost > 0:
        _, terrain_data = terrain.get_province_terrain(province_id)
        if 'nation_designer_cost_multiplier' in terrain_data:
            cost *= terrain_data['nation_designer_cost_multiplier']

    if 'trade_goods' in province and province['trade_goods'] == 'gold':
        cost += province['base_production'] * 3.0

    if 'extra_cost' in province:
        cost += province['extra_cost']
        
    if cost > 0:
        return cost
    else:
        return None
