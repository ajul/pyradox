import _initpath
import re
import os
import pyradox.hoi4.tech
import pyradox.hoi4.unit
import pyradox.format
import pyradox.struct
import pyradox.wiki
import pyradox.yml

def computeCountryTagAndName(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

countries = {}

for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    tag, name = computeCountryTagAndName(filename)
    country['tag'] = tag
    rulingParty = country['set_politics']['ruling_party'] or 'neutrality'
    country['name'] = pyradox.yml.getLocalization('%s_%s' % (tag, rulingParty), ['countries'], game = 'HoI4')
    if country['name'] is None: print(tag)
    countries[tag] = country

advisorTypes = [
    'political_advisor',
    ]

companyTypes = [
    'tank_manufacturer',
    'naval_manufacturer',
    'aircraft_manufacturer',
    'materiel_manufacturer',
    'industrial_concern',
    ]

theoristTypes = [
    'theorist',
    ]
    
militaryChiefTypes = [
    'army_chief',
    'navy_chief',
    'air_chief',
]

militaryHighCommandTypes = [
    'high_command',
    ]

typesToTabulate = militaryChiefTypes

result = pyradox.struct.Tree()


ideaData = pyradox.txt.parseMerge(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'ideas'), mergeLevels = 2)['ideas']
for ideaType in typesToTabulate:
    ideas = ideaData[ideaType]
    typeName = pyradox.yml.getLocalization(ideaType, ['ideas', 'traits'], game = 'HoI4')
    for ideaKey, idea in ideas.items():
        if ideaKey == 'designer': continue
        row = pyradox.struct.Tree()
        row['type'] = typeName
        
        if 'allowed' not in idea:
            row['country'] = 'Generic'
        elif 'tag' in idea['allowed']:
            row['tag'] = idea['allowed']['tag']
            row['country'] = '{{flag|%s}}' % countries[idea['allowed']['tag']]['name']
        elif 'original_tag' in idea['allowed']:
            row['country'] = '{{flag|%s}}' % countries[idea['allowed']['original_tag']]['name']
            # row['country'] += ' and successors'
        elif len(idea['allowed']) == 1 and 'or' in idea['allowed']:
            allowed = ['{{flag|%s}}' % countries[tag]['name'] for tag in idea['allowed']['or'].values()]
            row['country'] = '<br/>'.join(allowed)
        else:
            print('\nUnhandled case.')
            print(idea)
            row['country'] = 'Generic'

        row['name'] = pyradox.yml.getLocalization(ideaKey, ['ideas', 'focus'], game = 'HoI4') or (
            row['tag'] and pyradox.yml.getLocalization('%s_%s' % (row['tag'], ideaKey), ['ideas'], game = 'HoI4')
            )

        if 'research_bonus' in idea:
            row['research_bonus'] = idea['research_bonus']
        if 'equipment_bonus' in idea:
            row['equipment_bonus'] = idea['equipment_bonus']
        for trait in idea.findAll('traits'):
            row.append('traits', trait)
        row['trait_display'] = '<br/>'.join(
            pyradox.yml.getLocalization(traitKey, ['ideas', 'traits'], game = 'HoI4') for traitKey in idea.findAll('traits')).replace('\\n', ' ')
        result.append(ideaKey, row)

traits = pyradox.txt.parseFile(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'country_leader', '00_traits.txt'))['leader_traits']

def computeEffectString(effectKey, magnitude):
    if effectKey in ['sprite', 'random']: return ''
    if effectKey == 'equipment_bonus':
        result = ''
        for k, v in magnitude.items():
            result += computeEffectString(k, v)
        return result

nonPercentModifiers = [
    'communism_drift',
    'democratic_drift',
    'fascism_drift',
    'experience_gain_army',
    'experience_gain_air',
    'experience_gain_navy',
    ]

trueColor = [
    'unity_weekly',
    'armor_value',
    'attack',
    'carrier_size',
    'naval_range',
    'naval_speed',
    ]

falseColor = [
    'partisan_effect',
    'build_cost_ic',
    'sub_visibility',
    'surface_visibility',
    ]

def computeMagnitudeString(effectKey, magnitude, forceColor = None):
    if effectKey in nonPercentModifiers:
        return '{{green|%+0.2f}}' % magnitude
    else:
        if forceColor is not None:
            color = forceColor
        elif effectKey in trueColor:
            color = True
        elif effectKey in falseColor:
            color = False
        else:
            color = 'green'
        return pyradox.wiki.coloredPercentString(magnitude, numberFormat = '%+0.1f%%', color = color)

# hacky: put each trait we see into a tree
traitResult = pyradox.struct.Tree()

def computeEffects(k, v):
    result = '<ul>'

    def equipmentBonus(equipmentBonuses):
        result = ''
        for equipmentType, effects in equipmentBonuses.items():
            equipmentTypeName = (
                pyradox.yml.getLocalization(equipmentType, ['equipment', 'equip_air', 'equip_naval'], game = 'HoI4') or pyradox.format.humanTitle(equipmentType)
                or pyradox.format.humanTitle(equipmentType))
            for effectKey, magnitude in effects.items():
                effectName = pyradox.yml.getLocalization('modifier_' + effectKey, ['modifiers'], game = 'HoI4') or pyradox.format.humanTitle(effectKey)
                magnitudeString = computeMagnitudeString(effectKey, magnitude)
                result += '<li>%s %s: %s</li>' % (equipmentTypeName, effectName, magnitudeString)
        return result

    if 'research_bonus' in v:
        for category, magnitude in v['research_bonus'].items():
            categoryString = pyradox.yml.getLocalization(category + '_research', ['modifiers'], game = 'HoI4') or (
                pyradox.format.humanTitle(category) + ' Research Time')
            magnitudeString = computeMagnitudeString(category, -magnitude, False)
            result += '<li>%s: %s</li>' % (categoryString, magnitudeString)

    if 'equipment_bonus' in v:
        result += equipmentBonus(v['equipment_bonus'])
    
    for traitKey in v.findAll('traits'):
        trait = traits[traitKey]
        subresult = ''
        for effectKey, magnitude in trait.items():
            if effectKey in ['sprite', 'random', 'ai_will_do']: continue
            elif effectKey == 'equipment_bonus':
                subresult += equipmentBonus(magnitude)
            else:
                effectName = pyradox.yml.getLocalization('modifier_' + effectKey, ['modifiers'], game = 'HoI4') or pyradox.format.humanTitle(effectKey)
                magnitudeString = computeMagnitudeString(effectKey, magnitude)
                subresult += '<li>%s: %s</li>' % (effectName, magnitudeString)
        if traitKey not in traitResult.keys():
            row = pyradox.struct.Tree()
            row['name'] = pyradox.yml.getLocalization(traitKey, ['ideas', 'traits'], game = 'HoI4').replace('\\n', ' ')
            row['type'] = v['type']
            row['text'] = '<ul>' + subresult + '</ul>'
            
            traitResult[traitKey] = row
        result += subresult
    result += '</ul>'
    return result

columns = [
    ('Name', '%(name)s', None),
    ('Country', '%(country)s', None),
    ('Type', '%(type)s', None),
    ('Trait', '%(trait_display)s', None),
    ('Effects', computeEffects, None),
    ]

if len(typesToTabulate) == 1:
    columns = [x for x in columns if x[0] != 'Type']

out = open("out/ideas.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.wiki.makeWikitable(result, columns, sortFunction = lambda item: item[1]['country'], tableStyle = None))
out.close()

traitColumns = [
    ('Trait', '%(name)s', None),
    ('Effects', '%(text)s', None),
    ]

out = open("out/traits.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.wiki.makeWikitable(traitResult, traitColumns, sortFunction = lambda item: item[1]['name'], tableStyle = None))
out.close()
