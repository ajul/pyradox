import _initpath
import os
import hoi4

import pyradox

techs = hoi4.load.get_technologies()

# child tech -> [parent_tech, ...]
techs_or_dependencies = {}

for tech_key, tech in techs.items():
    if isinstance(tech, pyradox.Tree):
        for path in tech.find_all('path'):
            child_tech_key = path['leads_to_tech']
            if child_tech_key not in techs_or_dependencies:
                techs_or_dependencies[child_tech_key] = []
            techs_or_dependencies[child_tech_key].append(tech_key)

def check_deps(tech_keys, filename, date):
    for tech_key in tech_keys:
        tech = techs[tech_key]
        if 'xor' in tech:
            for other_tech_key in tech['xor']:
                if other_tech_key in tech_keys:
                    print('%s : %s : Tech %s violates mutual exclusivity with: %s' % (filename, date, tech_key, other_tech_key))
        if 'dependencies' in tech:
            for other_tech_key in tech['dependencies']:
                if other_tech_key not in tech_keys:
                    print('%s : %s : Tech %s is missing prerequisite: %s' % (filename, date, tech_key, other_tech_key))

        if tech_key in techs_or_dependencies:
            ancestors = list(techs_or_dependencies[tech_key])
            researched_ancestors = []
            while len(ancestors) > 0:
                ancestor = ancestors.pop()
                if ancestor in tech_keys:
                    # found root tech
                    if ancestor not in techs_or_dependencies: break
                    # otherwise dig further
                    researched_ancestors.append(ancestor)
                    ancestors += list(techs_or_dependencies[ancestor])
            else:
                print_string = '%s : %s : Tech %s is missing prerequsite' % (filename, date, tech_key)
                if len(researched_ancestors) > 0:
                    print_string += ' via: '
                    for other_tech_key in researched_ancestors:
                        print_string += other_tech_key + ', '
                    print_string = print_string[:-2] + '.'
                else:
                    print_string += ', needs one of: '
                    for other_tech_key in techs_or_dependencies[tech_key]:
                        print_string += other_tech_key + ', '
                    print_string = print_string[:-2] + '.'
                print(print_string)

def check_years(tech_keys, filename, date):
    for tech_key in tech_keys:
        tech = techs[tech_key]
        if (tech['start_year'] or 0) > date.year:
            print('%s : %s : Tech %s is ahead of time with year %s' % (filename, date, tech_key, tech['start_year']))

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'countries')):
    tech_keys = set(country['set_technology'].keys())
    check_deps(tech_keys, filename, pyradox.Date('1936.1.1'))
    for date, effects in country.items():
        if not isinstance(date, pyradox.Date): continue
        if 'set_technology' not in effects: continue
        tech_keys |= set(effects['set_technology'].keys())
        check_deps(tech_keys, filename, date)

for filename, country in pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'countries')):
    tech_keys = set(country['set_technology'].keys())
    check_years(tech_keys, filename, pyradox.Date('1936.1.1'))
    for date, effects in country.items():
        if not isinstance(date, pyradox.Date): continue
        if 'set_technology' not in effects: continue
        tech_keys |= set(effects['set_technology'].keys())
        check_years(tech_keys, filename, date)
