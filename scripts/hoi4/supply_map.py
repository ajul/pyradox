import _initpath
import os
import math
import re
import collections
import pyradox.config
import pyradox.txt
import pyradox.worldmap
import pyradox.image
from PIL import Image

scale = 2.0

# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.config.get_basedir('HoI4'), 'history', 'states'), verbose=False)
supply_areas = pyradox.txt.parse_merge(os.path.join(pyradox.config.get_basedir('HoI4'), 'map', 'supplyareas'), verbose=False)

states_by_id = {state['id'] : state for state in states.values()}

# supply_area_id -> province_id_s
supply_area_provinces = {}
supply_area_local_supply = {}
supply_area_transport = {}

for supply_area in supply_areas.values():
    supply_area_provinces[supply_area['id']] = []
    
    total_infrastructure = 0
    total__vps_upply = 0
    total_naval_base = 0
    
    for state_id in supply_area.find_all('states'):
        state = states_by_id[state_id]
        if 'buildings' in state['history']:
            total_infrastructure += state['history']['buildings']['infrastructure']
            for k, v in state['history']['buildings'].items():
                if isinstance(k, int):
                    total_naval_base += v['naval_base'] or 0
        
        for province_id in state.find_all('provinces'):
            supply_area_provinces[supply_area['id']].append(province_id)

        for _, vp_value in state['history'].find_all('victory_points', tuple_length = 2):
            total__vps_upply += math.floor(vp_value * 0.1 + 1)
            
    average_infrastructure = total_infrastructure / supply_area.count('states')
    infrastructure_transport = 2.0 * (average_infrastructure ** 2.0)
    naval_transport = 3.0 * total_naval_base
    transport = max(infrastructure_transport, naval_transport)
    
    local_supply = supply_area['value'] + total__vps_upply
    supply_area_local_supply[supply_area['id']] = local_supply
    supply_area_transport[supply_area['id']] = transport

province_map = pyradox.worldmap.ProvinceMap(basedir = pyradox.config.get_basedir('HoI4'))

# provinces -> state id
groups_local = {}
colormap_local = {}
groups_transport = {}
colormap_transport = {}

for supply_area_id, provinces in supply_area_provinces.items():
    local_supply = supply_area_local_supply[supply_area_id]
    transport = supply_area_transport[supply_area_id]
    k = []
    for province_id in provinces:
        if not province_map.is_water_province(province_id):
            k.append(province_id)
            colormap_local[province_id] = pyradox.image.colormap_red_green(local_supply / 25)
            colormap_transport[province_id] = pyradox.image.colormap_red_green(transport / 100)
    k = tuple(x for x in k)
    groups_local[k] = '%d' % local_supply
    groups_transport[k] = '%d' % transport

local_image = province_map.generate_image(colormap_local, default_land_color=(255, 255, 255), edge_color=(63, 63, 63), edge_groups = groups_local.keys())
province_map.overlay_text(local_image, groups_local, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
local_image.save('out/local_supply_map.png')

transport_image = province_map.generate_image(colormap_transport, default_land_color=(255, 255, 255), edge_color=(63, 63, 63), edge_groups = groups_transport.keys())
province_map.overlay_text(transport_image, groups_transport, fontfile = "tahoma.ttf", fontsize = 9, antialias = False)
transport_image.save('out/transport_supply_map.png')

