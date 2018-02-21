import _initpath
import os



import pyradox


import ideaoptions

# format: idea -> tree
existing_ideas = {}

# format: bonus -> [(title, value)...]
bonus_sources = {}

localization_sources = ['powers_and_ideas', 'nw2', 'res_publica', "aow", 'eldorado', 'common_sense']

def add_bonus(bonus, title, value):
    if bonus not in bonus_sources:
        bonus_sources[bonus] = []
    bonus_sources[bonus].append((value, title))

def value_string(bonus, value):
    if bonus not in ideaoptions.bonus_types: print(bonus)
    if ideaoptions.is_beneficial(bonus, value):
        color = "green"
    else:
        color = "red"
    if ideaoptions.is_percent_bonus(bonus):
        return '{{%s|%+0.1f%%}}' % (color, value * 100.0)
    elif isinstance(value, int):
        return '{{%s|%+d}}'% (color, value)
    elif isinstance(value, float):
        return '{{%s|%+0.2f}}'% (color, value)
    else:
        return '{{%s|%s}}' % (color, pyradox.make_token_string(value))

def process_idea_group(key, tree):
    # if 'free' not in tree or not tree['free']: return # free groups only
    
    ig_name = pyradox.yml.get_localization(key)

    if 'start' in tree:
        traditions = tree['start']
        title = pyradox.yml.get_localization('%s_start' % key) or key
        for bonus, value in traditions.items():
            add_bonus(bonus, title, value)

    ambitions = tree['bonus']
    title = pyradox.yml.get_localization('%s_bonus' % key) or key
    for bonus, value in ambitions.items():
        add_bonus(bonus, title, value)

    idx = 1
    for idea, bonuses in tree.items():
        if idea in ('start', 'bonus', 'free', 'trigger', 'ai_will_do', 'category', 'important'): continue
        if idea in existing_ideas:
            bonuses = existing_ideas[idea]
        else:
            existing_ideas[idea] = bonuses
        idea_name = pyradox.yml.get_localization(idea)
        title = '%s %d: %s' % (ig_name, idx, idea_name)
        for bonus, value in bonuses.items():
            add_bonus(bonus, title, value)
        idx += 1

def make_wiki_table(bonus):
    result = '<table class = "wikitable sortable">\n'
    result += '    <tr><th width="400px">Idea</th><th>Modifier</th></tr>\n'

    for value, title in bonus_sources[bonus]:
        result += '    <tr><td>%s</td><td>%s</td></tr>\n' % (title, value_string(bonus, value))
    result += '</table>\n'
    return result

for _, data in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('EU4'), 'common', 'ideas')):
    for key, tree in data.items():
        process_idea_group(key, tree)

for bonus in ideaoptions.bonus_types:
    if bonus not in bonus_sources.keys():
        print("No sources:" + bonus)

print()

wiki_page = ''
for bonus in sorted(bonus_sources.keys()):
    sources = ['EU4', 'text', 'modifers', 'powers_and_ideas', 'nw2', 'res_publica', "aow"]
    bonus_title = (
        pyradox.yml.get_localization('modifier_%s' % bonus)
        or pyradox.yml.get_localization('yearly_%s' % bonus)
        or pyradox.yml.get_localization(bonus)
        )
    if not bonus_title:
        print("Missing title:" + bonus)
        bonus_title = pyradox.format.human_title(bonus)
    
    wiki_page += '==[[File:%s.png]] %s ==\n' % (bonus, bonus_title)
    wiki_page += make_wiki_table(bonus)

f = open('out/reverse_unis.txt', 'w', encoding='cp1252')
f.write(wiki_page)
f.close()

wiki_template = '<includeonly>{{#switch: {{lc:{{{1}}}}}\n'

for bonus in sorted(bonus_sources.keys()):
    wiki_template += '| %s =   ' % bonus
    reverse = not ideaoptions.is_reversed(bonus)
    prev_value = None
    for value, title in sorted(bonus_sources[bonus], reverse=reverse):
        if value != prev_value:
            prev_value = value
            wiki_template = wiki_template[:-2]
            wiki_template += '\n{{{2|*}}} %s: ' % value_string(bonus, value)
        wiki_template += title + ', '

    wiki_template = wiki_template[:-2] + '\n'

wiki_template += '| default (invalid bonus type {{lc:{{{1}}}}})\n'
wiki_template += '}}</includeonly><noinclude>{{template doc}}</noinclude>'

f = open('out/reverse_unis_list_template.txt', 'w', encoding='cp1252')
f.write(wiki_template)
f.close()

wiki_template = '<includeonly>{{#switch: {{lc:{{{1}}}}}\n'

for bonus in sorted(bonus_sources.keys()):
    wiki_template += '| %s = %s' % (bonus, make_wiki_table(bonus))

wiki_template += '| default (invalid bonus type {{lc:{{{1}}}}})\n'
wiki_template += '}}</includeonly><noinclude>{{template doc}}</noinclude>'

f = open('out/reverse_unis_table_template.txt', 'w', encoding='cp1252')
f.write(wiki_template)
f.close()
