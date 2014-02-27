import _initpath
import os
import pyradox.config
import pyradox.txt
import pyradox.worldmap

colormap = {}
tree = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'decisions', 'Muslim.txt'))
unifyRequirements = tree['country_decisions']['unify_islam']['allow']
for provinceID in unifyRequirements.findAll('owns_or_vassal_of'):
    colormap[provinceID] = (0, 127, 0)
        
provinceMap = pyradox.worldmap.ProvinceMap()
out = provinceMap.generateImage(colormap)
out.save('out/unify_islam_map.png')
