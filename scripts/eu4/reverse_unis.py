import _initpath
import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml

import ideaoptions

# format: idea -> tree
existingIdeas = {}

# format: bonus -> [(title, value)...]
bonusSources = {}

localizationSources = ['powers_and_ideas', 'nw2', 'res_publica', "aow", 'eldorado', 'common_sense']

def addBonus(bonus, title, value):
    if bonus not in bonusSources:
        bonusSources[bonus] = []
    bonusSources[bonus].append((value, title))

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

def processIdeaGroup(key, tree):
    # if 'free' not in tree or not tree['free']: return # free groups only
    
    igName = pyradox.yml.getLocalization(key, localizationSources)

    if 'start' in tree:
        traditions = tree['start']
        title = pyradox.yml.getLocalization('%s_start' % key, localizationSources) or key
        for bonus, value in traditions.items():
            addBonus(bonus, title, value)

    ambitions = tree['bonus']
    title = pyradox.yml.getLocalization('%s_bonus' % key, localizationSources) or key
    for bonus, value in ambitions.items():
        addBonus(bonus, title, value)

    idx = 1
    for idea, bonuses in tree.items():
        if idea in ('start', 'bonus', 'free', 'trigger', 'ai_will_do', 'category', 'important'): continue
        if idea in existingIdeas:
            bonuses = existingIdeas[idea]
        else:
            existingIdeas[idea] = bonuses
        ideaName = pyradox.yml.getLocalization(idea, localizationSources)
        title = '%s %d: %s' % (igName, idx, ideaName)
        for bonus, value in bonuses.items():
            addBonus(bonus, title, value)
        idx += 1

def makeWikiTable(bonus):
    result = '<table class = "wikitable sortable">\n'
    result += '    <tr><th width="400px">Idea</th><th>Modifier</th></tr>\n'

    for value, title in bonusSources[bonus]:
        result += '    <tr><td>%s</td><td>%s</td></tr>\n' % (title, valueString(bonus, value))
    result += '</table>\n'
    return result

for _, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'ideas')):
    for key, tree in data.items():
        processIdeaGroup(key, tree)

for bonus in ideaoptions.bonusTypes:
    if bonus not in bonusSources.keys():
        print("No sources:" + bonus)

print()

wikiPage = ''
for bonus in sorted(bonusSources.keys()):
    sources = ['EU4', 'text', 'modifers', 'powers_and_ideas', 'nw2', 'res_publica', "aow"]
    bonusTitle = (
        pyradox.yml.getLocalization('modifier_%s' % bonus, sources)
        or pyradox.yml.getLocalization('yearly_%s' % bonus, sources)
        or pyradox.yml.getLocalization(bonus, sources)
        )
    if not bonusTitle:
        print("Missing title:" + bonus)
        bonusTitle = pyradox.format.humanTitle(bonus)
    
    wikiPage += '==[[File:%s.png]] %s ==\n' % (bonus, bonusTitle)
    wikiPage += makeWikiTable(bonus)

f = open('out/reverse_unis.txt', 'w', encoding='cp1252')
f.write(wikiPage)
f.close()

wikiTemplate = '<includeonly>{{#switch: {{lc:{{{1}}}}}\n'

for bonus in sorted(bonusSources.keys()):
    wikiTemplate += '| %s =   ' % bonus
    reverse = not ideaoptions.isReversed(bonus)
    prevValue = None
    for value, title in sorted(bonusSources[bonus], reverse=reverse):
        if value != prevValue:
            prevValue = value
            wikiTemplate = wikiTemplate[:-2]
            wikiTemplate += '\n{{{2|*}}} %s: ' % valueString(bonus, value)
        wikiTemplate += title + ', '

    wikiTemplate = wikiTemplate[:-2] + '\n'

wikiTemplate += '| default (invalid bonus type {{lc:{{{1}}}}})\n'
wikiTemplate += '}}</includeonly><noinclude>{{template doc}}</noinclude>'

f = open('out/reverse_unis_list_template.txt', 'w', encoding='cp1252')
f.write(wikiTemplate)
f.close()

wikiTemplate = '<includeonly>{{#switch: {{lc:{{{1}}}}}\n'

for bonus in sorted(bonusSources.keys()):
    wikiTemplate += '| %s = %s' % (bonus, makeWikiTable(bonus))

wikiTemplate += '| default (invalid bonus type {{lc:{{{1}}}}})\n'
wikiTemplate += '}}</includeonly><noinclude>{{template doc}}</noinclude>'

f = open('out/reverse_unis_table_template.txt', 'w', encoding='cp1252')
f.write(wikiTemplate)
f.close()
