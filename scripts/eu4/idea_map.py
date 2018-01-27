import _initpath
import os
import pyradox.config
import pyradox.format

import pyradox
import pyradox.yml


result_tree = pyradox.Tree()

for group_name, group_data in pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('EU4'), 'common', 'ideas')).items():
    if 'trigger' not in group_data: continue
    trigger = group_data['trigger']
    for tag in trigger.find_all('tag'):
        result_tree[tag] = group_name
    if 'or' in trigger:
        for tag in trigger['or'].find_all('tag'):
            result_tree[tag] = group_name

outfile = open('out/idea_map.txt', mode = 'w')
outfile.write(str(result_tree))
outfile.close()
