import _initpath
import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml


resultTree = pyradox.struct.Tree()

for groupName, groupData in pyradox.txt.parseMerge(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'ideas')).items():
    if 'trigger' not in groupData: continue
    trigger = groupData['trigger']
    for tag in trigger.findAll('tag'):
        resultTree[tag] = groupName
    if 'or' in trigger:
        for tag in trigger['or'].findAll('tag'):
            resultTree[tag] = groupName

outfile = open('out/idea_map.txt', mode = 'w')
outfile.write(str(resultTree))
outfile.close()
