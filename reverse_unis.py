import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml

# format: bonus -> [(title, value)...]
bonusSources = {}

def addBonus(bonus, title, value):
    if bonus not in bonusSources:
        bonusSources[bonus] = []
    bonusSources[bonus].append((title, value))

def processIdeaGroup(key, tree):
    if 'free' not in tree or not tree['free']: return # free groups only
    
    igName = pyradox.yml.getLocalization(key, 'powers_and_ideas')
    
    traditions = tree['start']
    title = pyradox.yml.getLocalization('%s_start' % key, 'powers_and_ideas') or key
    for bonus, value in traditions.items():
        addBonus(bonus, title, value)

    ambitions = tree['bonus']
    title = pyradox.yml.getLocalization('%s_bonus' % key, 'powers_and_ideas') or key
    for bonus, value in ambitions.items():
        addBonus(bonus, title, value)

    idx = 1
    for idea, bonuses in tree.items():
        if idea in ('start', 'bonus', 'free', 'trigger'): continue
        ideaName = pyradox.yml.getLocalization(idea, 'powers_and_ideas')
        title = '%s %d: %s' % (igName, idx, ideaName)
        for bonus, value in bonuses.items():
            addBonus(bonus, title, value)
        idx += 1

def makeWikiTable(bonus):
    result = '{|class = "wikitable sortable"\n'
    result += '! width="400px" | Idea !! Modifier \n'

    for title, value in bonusSources[bonus]:
        result += '|-\n'
        result += '| %s || %s \n' % (title, pyradox.primitive.makeTokenString(value))
    result += '|}\n'
    return result

for _, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'ideas')):
    for key, tree in data.items():
        processIdeaGroup(key, tree)

wikiPage = ''
for bonus in sorted(bonusSources.keys()):
    sources = ['EU4', 'text', 'modifers', 'powers_and_ideas']
    bonusTitle = (
        pyradox.yml.getLocalization('modifier_%s' % bonus, sources)
        or pyradox.yml.getLocalization('yearly_%s' % bonus, sources)
        or pyradox.yml.getLocalization(bonus, sources)
        )
    if not bonusTitle:
        print(bonus)
        bonusTitle = pyradox.format.humanTitle(bonus)
    
    wikiPage += '==[[File:%s.png]] %s ==\n' % (bonus, bonusTitle)
    wikiPage += makeWikiTable(bonus)

f = open('out/reverse_unis.txt', 'w', encoding='utf-8')
f.write(wikiPage)
f.close()

wikiTemplate = '<includeonly>{{#switch: {{lc:{{{1}}}}}\n'

for bonus in sorted(bonusSources.keys()):
    wikiTemplate += '| %s = \n' % bonus
    for title, value in bonusSources[bonus]:
        wikiFormatString = '{{#ifeq:{{{3|}}}|%%|%+d%%|%+s}}' % (value * 100.0, value)
        wikiTemplate += '{{{2|*}}} %s: {{green|%s}}\n' % (title, wikiFormatString)

wikiTemplate += '| default (invalid bonus type {{lc:{{{1}}}}})\n'
wikiTemplate += '}}</includeonly><noinclude>{{template doc}}</noinclude>'

f = open('out/reverse_unis_list_template.txt', 'w', encoding='utf-8')
f.write(wikiTemplate)
f.close()

wikiTemplate = '<includeonly>{{#switch: {{lc:{{{1}}}}}\n'

for bonus in sorted(bonusSources.keys()):
    wikiTemplate += '| %s = %s' % (bonus, makeWikiTable(bonus).replace('|', '{{!}}'))

wikiTemplate += '| default (invalid bonus type {{lc:{{{1}}}}})\n'
wikiTemplate += '}}</includeonly><noinclude>{{template doc}}</noinclude>'

f = open('out/reverse_unis_table_template.txt', 'w', encoding='utf-8')
f.write(wikiTemplate)
f.close()
