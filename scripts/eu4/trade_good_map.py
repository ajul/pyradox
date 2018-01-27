import _initpath
import os
import re
import collections
import pyradox


basedir = r'D:\Steam\steamapps\common\Europa Universalis IV'

trade_good_colors = collections.OrderedDict([
    ('grain' , (255, 255, 127)),        # pale yellow
    ('wine' , (127, 0, 255)),           # purple
    ('wool' , (255, 127, 255)),         # pale magenta
    ('cloth' , (255, 0, 255)),          # magenta
    ('fish' , (0, 0, 127)),             # dark blue    
    ('fur' , (191, 63, 0)),             # dark orange
    ('salt' , (191, 191, 191)),         # light gray
    ('naval_supplies' , (0, 0, 255)),   # blue
    
    ('copper' , (255, 127, 0)),         # bright orange
    ('gold' , (255, 191, 0)),           # yellow
    ('iron' , (191, 191, 255)),         # light blue
    
    ('slaves' , (0, 0, 0)),             # black
    ('ivory' , (255, 255, 255)),        # white
    
    ('tea' , (0, 255, 0)),              # green
    ('chinaware' , (0, 127, 255)),      # teal blue
    ('spices' , (255, 0, 0)),           # red

    ('coffee' , (127, 63, 0)),          # dark brown
    ('cotton' , (191, 255, 191)),       # pale green    
    ('sugar' , (127, 255, 255)),        # pale teal
    ('tobacco' , (0, 63, 0)),           # dark green

    ('unknown' , (127, 127, 127)),         # gray
    ])

legend = ''
for trade_good, color in trade_good_colors.items():
    bg_color_string = '#%02x%02x%02x' % color
    r, g, b = color
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if y >= 255 / 2:
        text_color_string = '#000000'
    else:
        text_color_string = '#ffffff'
    legend += '<span style="color:%s; background-color:%s">%s </span>' % (text_color_string, bg_color_string, trade_good)

print(legend)

colormap = {}
for filename, data in pyradox.txt.parse_dir(os.path.join(basedir, 'history', 'provinces'), verbose=False):
    m = re.match('\d+', filename)
    province_id = int(m.group(0))
    if 'trade_goods' in data:
        colormap[province_id] = trade_good_colors[data['trade_goods']]
        
province_map = pyradox.worldmap.ProvinceMap(basedir)
out = province_map.generate_image(colormap)
out.save('out/trade_good_map.png')


