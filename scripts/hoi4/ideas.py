import _initpath
import re
import os
import hoi4


import pyradox



def compute_country_tag_and_name(filename):
    m = re.match('.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

countries = {}

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'countries')):
    tag, name = compute_country_tag_and_name(filename)
    country['tag'] = tag
    ruling_party = country['set_politics']['ruling_party'] or 'neutrality'
    country['name'] = pyradox.yml.get_localization('%s_%s' % (tag, ruling_party), ['countries'], game = 'HoI4')
    if country['name'] is None: print(tag)
    countries[tag] = country

advisor_types = [
    'political_advisor',
    ]

company_types = [
    'tank_manufacturer',
    'naval_manufacturer',
    'aircraft_manufacturer',
    'materiel_manufacturer',
    'industrial_concern',
    ]

theorist_types = [
    'theorist',
    ]
    
military_chief_types = [
    'army_chief',
    'navy_chief',
    'air_chief',
]

military_high_command_types = [
    'high_command',
    ]

types_to_tabulate = military_chief_types

result = pyradox.Tree()


idea_data = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'ideas'), merge_levels = 2)['ideas']
for idea_type in types_to_tabulate:
    ideas = idea_data[idea_type]
    type_name = pyradox.yml.get_localization(idea_type, ['ideas', 'traits'], game = 'HoI4')
    for idea_key, idea in ideas.items():
        if idea_key == 'designer': continue
        row = pyradox.Tree()
        row['type'] = type_name
        
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
            print('\n_unhandled case.')
            print(idea)
            row['country'] = 'Generic'

        row['name'] = pyradox.yml.get_localization(idea_key, ['ideas', 'focus'], game = 'HoI4') or (
            row['tag'] and pyradox.yml.get_localization('%s_%s' % (row['tag'], idea_key), ['ideas'], game = 'HoI4')
            )

        if 'research_bonus' in idea:
            row['research_bonus'] = idea['research_bonus']
        if 'equipment_bonus' in idea:
            row['equipment_bonus'] = idea['equipment_bonus']
        for trait in idea.find_all('traits'):
            row.append('traits', trait)
        row['trait_display'] = '<br/>'.join(
            pyradox.yml.get_localization(trait_key, ['ideas', 'traits'], game = 'HoI4') for trait_key in idea.find_all('traits')).replace('\\n', ' ')
        result.append(idea_key, row)

traits = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'country_leader', '00_traits.txt'))['leader_traits']

def compute_effect_string(effect_key, magnitude):
    if effect_key in ['sprite', 'random']: return ''
    if effect_key == 'equipment_bonus':
        result = ''
        for k, v in magnitude.items():
            result += compute_effect_string(k, v)
        return result

non_percent_modifiers = [
    'communism_drift',
    'democratic_drift',
    'fascism_drift',
    'experience_gain_army',
    'experience_gain_air',
    'experience_gain_navy',
    ]

true_color = [
    'unity_weekly',
    'armor_value',
    'attack',
    'carrier_size',
    'naval_range',
    'naval_speed',
    ]

false_color = [
    'partisan_effect',
    'build_cost_ic',
    'sub_visibility',
    'surface_visibility',
    ]

def compute_magnitude_string(effect_key, magnitude, force_color = None):
    if effect_key in non_percent_modifiers:
        return '{{green|%+0.2f}}' % magnitude
    else:
        if force_color is not None:
            color = force_color
        elif effect_key in true_color:
            color = True
        elif effect_key in false_color:
            color = False
        else:
            color = 'green'
        return pyradox.wiki.colored_percent_string(magnitude, number_format = '%+0.1f%%', color = color)

# hacky: put each trait we see into a tree
trait_result = pyradox.Tree()

def compute_effects(k, v):
    result = '<ul>'

    def equipment_bonus(equipment_bonuses):
        result = ''
        for equipment_type, effects in equipment_bonuses.items():
            equipment_type_name = (
                pyradox.yml.get_localization(equipment_type, ['equipment', 'equip_air', 'equip_naval'], game = 'HoI4') or pyradox.format.human_title(equipment_type)
                or pyradox.format.human_title(equipment_type))
            for effect_key, magnitude in effects.items():
                effect_name = pyradox.yml.get_localization('modifier_' + effect_key, ['modifiers'], game = 'HoI4') or pyradox.format.human_title(effect_key)
                magnitude_string = compute_magnitude_string(effect_key, magnitude)
                result += '<li>%s %s: %s</li>' % (equipment_type_name, effect_name, magnitude_string)
        return result

    if 'research_bonus' in v:
        for category, magnitude in v['research_bonus'].items():
            category_string = pyradox.yml.get_localization(category + '_research', ['modifiers'], game = 'HoI4') or (
                pyradox.format.human_title(category) + ' Research Time')
            magnitude_string = compute_magnitude_string(category, -magnitude, False)
            result += '<li>%s: %s</li>' % (category_string, magnitude_string)

    if 'equipment_bonus' in v:
        result += equipment_bonus(v['equipment_bonus'])
    
    for trait_key in v.find_all('traits'):
        trait = traits[trait_key]
        subresult = ''
        for effect_key, magnitude in trait.items():
            if effect_key in ['sprite', 'random', 'ai_will_do']: continue
            elif effect_key == 'equipment_bonus':
                subresult += equipment_bonus(magnitude)
            else:
                effect_name = pyradox.yml.get_localization('modifier_' + effect_key, ['modifiers'], game = 'HoI4') or pyradox.format.human_title(effect_key)
                magnitude_string = compute_magnitude_string(effect_key, magnitude)
                subresult += '<li>%s: %s</li>' % (effect_name, magnitude_string)
        if trait_key not in trait_result.keys():
            row = pyradox.Tree()
            row['name'] = pyradox.yml.get_localization(trait_key, ['ideas', 'traits'], game = 'HoI4').replace('\\n', ' ')
            row['type'] = v['type']
            row['text'] = '<ul>' + subresult + '</ul>'
            
            trait_result[trait_key] = row
        result += subresult
    result += '</ul>'
    return result

columns = [
    ('Name', '%(name)s', None),
    ('Country', '%(country)s', None),
    ('Type', '%(type)s', None),
    ('Trait', '%(trait_display)s', None),
    ('Effects', compute_effects, None),
    ]

if len(types_to_tabulate) == 1:
    columns = [x for x in columns if x[0] != 'Type']

out = open("out/ideas.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.wiki.make_wikitable(result, columns, sort_function = lambda key, value: value['country'], table_style = None))
out.close()

trait_columns = [
    ('Trait', '%(name)s', None),
    ('Effects', '%(text)s', None),
    ]

out = open("out/traits.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.wiki.make_wikitable(trait_result, trait_columns, sort_function = lambda key, value: value['name'], table_style = None))
out.close()
