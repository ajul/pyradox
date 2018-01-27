import _initpath
import os
import re
import math
import collections
import pyradox.config
import pyradox.image
import pyradox

import pyradox.worldmap

import load.province

import scipy.stats
# import province_costs

provinces = load.province.get_provinces()

def province_base_tax(province_id, province):
    if 'base_tax' in province and province['base_tax'] > 0:
        return province['base_tax']
    else:
        return None

def province_base_production(province_id, province):
    if 'base_production' in province and province['base_production'] > 0:
        return province['base_production']
    else:
        return None

def province_base_manpower(province_id, province):
    if 'base_manpower' in province and province['base_manpower'] > 0:
        return province['base_manpower']
    else:
        return None

def province_base_development(province_id, province):
    result = (
        (province_base_tax(province_id, province) or 0) +
        (province_base_production(province_id, province) or 0) +
        (province_base_manpower(province_id, province) or 0))
    if result > 0:
        return result
    else:
        return None

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
    
def native_population(province_id, province):
    if 'native_size' in province:
        return province['native_size'] / 10.0
    else:
        return None

def native_aggressiveness(province_id, province):
    if 'native_size' in province:
        return province['native_hostileness'] or 0
    else:
        return None

rank_method = 'dense'

def generate_map(province_function, filename, force_min = None):
    number_map = {int(re.match('\d+', filename).group(0)) :
                 province_function(int(re.match('\d+', filename).group(0)), province.at_date(pyradox.Date('1444.11.11')))
                 for filename, province in provinces.items()
                 if province_function(int(re.match('\d+', filename).group(0)), province) is not None}
    
    if force_min is None:
        force_min = min(number_map.values())

    effective_numbers = [max(x, force_min) for x in number_map.values()]
        
    ranks = scipy.stats.rankdata(effective_numbers, method = rank_method)
    min_rank = min(ranks)
    max_rank = max(ranks)
    range_rank = max_rank - min_rank
    colors = {}
    for number, rank in zip(number_map.values(), ranks):
        if number < force_min:
            colors[number] = pyradox.image.colormap_blue_red(0.0)
        else:
            colors[number] = pyradox.image.colormap_blue_red((rank - min_rank) / range_rank)
    color_map = {province_id : colors[number] for province_id, number in number_map.items()}
    text_map = {province_id : ('%d' % round(number)) for province_id, number in number_map.items()}

    province_map = pyradox.worldmap.ProvinceMap()
    image = province_map.generate_image(color_map)
    province_map.overlay_text(image, text_map, fontfile = "tahoma.ttf", default_font_color=(255, 255, 255), fontsize = 9, antialias = False)
    pyradox.image.save_using_palette(image, filename)
        
generate_map(province_base_tax, 'out/base_tax_map.png', force_min = 1.0)
generate_map(province_base_production, 'out/base_production_map.png', force_min = 1.0)
generate_map(province_base_manpower, 'out/base_manpower_map.png', force_min = 1.0)
generate_map(province_base_development, 'out/base_development_map.png', force_min = 3.0)
generate_map(province_cost, 'out/custom_nation_cost_map.png', force_min = 1.0)
# generate_map(native_population, 'out/native_population_map.png')
generate_map(native_aggressiveness, 'out/native_aggressiveness_map.png')



