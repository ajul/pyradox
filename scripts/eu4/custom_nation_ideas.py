import _initpath
import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml

import ideaoptions

def valueString(bonus, value):
    if bonus not in ideaoptions.bonusTypes: print(bonus)
    if ideaoptions.isBeneficial(bonus, value):
        color = "green"
    else:
        color = "red"
    if ideaoptions.isPercentBonus(bonus):
        return '{{%s|%+0.1f%%}}' % (color, value * 100.0)
    elif isinstance(value, int):
        return '{{%s|%+d}}'% (color, value)
    elif isinstance(value, float):
        return '{{%s|%+0.2f}}'% (color, value)
    else:
        return '{{%s|%s}}' % (color, pyradox.primitive.makeTokenString(value))

localizationSources = ['EU4', 'text', 'modifers']

default_max_level = 4

result = ''

result += '{|class = "wikitable sortable mw-collapsible mw-collapsed"\n'
result += '! rowspan = "2" | Bonus !! rowspan = "2" | Per level !! rowspan = "2" | Category !! colspan = "%d" | Cost \n' % default_max_level
result += '|-\n'
for i in range(default_max_level):
    result += '! %d !' % (i + 1)
result = result[:-1]
result += '\n'

for fileName, fileData in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'custom_ideas')):
    for ideaSet in fileData.values():
        # start category
        
        for idea, ideaData in ideaSet.items():
            if idea == 'category':
                powerType = ideaData.lower()
                continue

            # compile idea stats

            max_level = default_max_level
            costs = [0, 5, 15, 30] # cost indexed by level (0-based)
            for key, value in ideaData.items():
                if key in ('default', 'chance'):
                    continue
                elif key == 'max_level':
                    max_level = value
                elif 'level_cost_' in key:
                    level = int(key[len('level_cost_'):]) - 1
                    costs[level] = value
                else:
                    localizedKey = (
                        pyradox.yml.getLocalization('modifier_%s' % key, localizationSources)
                        or pyradox.yml.getLocalization('yearly_%s' % key, localizationSources)
                        or pyradox.yml.getLocalization(key, localizationSources)
                        )
                    if not localizedKey:
                        localizedKey = pyradox.format.humanTitle(key)
                        print("Missing title: " + key + ' => ' + localizedKey)
                    bonusValueString = valueString(key, value)

            # write to string
            result += '|-\n'
            result += '| %s || %s || {{icon|%s}} ' % (localizedKey, bonusValueString, powerType)
            for i in range(default_max_level):
                if i < max_level:
                    result += '|| %d ' % costs[i]
                else:
                    result += '|| '
            result += '\n'

result += '|}\n'

print(result)

