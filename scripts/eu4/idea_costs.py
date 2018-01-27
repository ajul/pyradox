import _initpath
import os
import pyradox.config
import pyradox.format

import pyradox
import pyradox.yml

import ideaoptions

def cost0_3(level):
    return 3 * (level - 1) * level / 2

def cost0_5(level):
    return 5 * (level - 1) * level / 2

cost_functions = {
    (0, 3) : cost0_3,
    (0, 5) : cost0_5,
    (0, 15) : lambda level: cost0_5(level * 2 - 1),
    (3, 18) : lambda level: cost0_3(level * 2),
    (5, 30) : lambda level: cost0_5(level * 2),
    (15, 50) : lambda level: cost0_5(level * 2 + 1),
    (30, 140) : lambda level: cost0_5(level * 4),
}

bonuses = {}

def eval_bonus(bonus_key, bonus_value):
    if bonus_key in bonuses:
        power_type, base_value, max_level, costs = bonuses[bonus_key]
        cost_function = cost_functions[costs]
        level = bonus_value / base_value
        return power_type, 10 * level / max_level, cost_function(level), costs[0] + (level - 1) * (costs[1] - costs[0])
    else:
        return None

for file_name, file_data in pyradox.txt.parse_dir(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'custom_ideas')):
    for idea_set in file_data.values():
        # start category
        
        for idea, idea_data in idea_set.items():
            if idea == 'category':
                power_type = idea_data.lower()
                continue

            costs = [0, 5] # cost indexed by level (0-based)
            max_level = 4
            for key, value in idea_data.items():
                if key in ('default', 'chance'):
                    continue
                elif key == 'max_level':
                    max_level = value
                elif 'level_cost_' in key:
                    level = int(key[len('level_cost_'):])
                    if level <= 2:
                        costs[level - 1] = value
                else:
                    bonus_key = key
                    base_value = value
            bonuses[bonus_key] = (power_type, base_value, max_level, tuple(costs))

result = '{|class = "wikitable sortable"\n'
result += '! Idea group !! Linear cost !! Base cost !! Adjusted for<br/>early ideas !! Max level ratio !! Final cost !! Bonuses unaccounted for\n'

result_tree = pyradox.Tree()

for file_name, file_data in pyradox.txt.parse_dir(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'ideas')):
    for idea_set_name, idea_set in file_data.items():
        
        index = 0
        base_cost = 0.0
        early_cost = 0.0
        total_linear_cost = 0.0
        unaccounted = [] # not appearing in designer
        level_counts = {
            'adm' : 0.0,
            'dip' : 0.0,
            'mil' : 0.0,
            }
        for key, value in idea_set.items():
            if key in ('category', 'trigger', 'free', 'ai_will_do', 'important'): continue
            
            if key == 'start':
                cost_multiplier = 2
            elif key == 'bonus':
                cost_multiplier = 1
            else:
                cost_multiplier = 2 - 0.2 * min(index, 5)
                index += 1

            for bonus_key, bonus_value in value.items():
                bonus_info = eval_bonus(bonus_key, bonus_value)
                if bonus_info is None:
                    unaccounted.append('%s (%s)' %( bonus_key, bonus_value))
                else:
                    power_type, level, cost, linear_cost = bonus_info
                    level_counts[power_type] += level
                    base_cost += cost
                    early_cost += cost * cost_multiplier
                    total_linear_cost += linear_cost

        max_ratio = max(level_counts.values()) / sum(level_counts.values())
        final_cost = early_cost * (1 + 5 * max(0, max_ratio - 0.5))
        unaccounted_string = '%d: %s' % (len(unaccounted), ', '.join(unaccounted))
        result += '|-\n'
        result += '| %s || %0.1f || %0.1f || %0.1f || %0.1f%% || %0.1f || %s \n' % (idea_set_name, total_linear_cost, base_cost, early_cost, max_ratio * 100, final_cost, unaccounted_string)

        idea_set_tree = pyradox.Tree()

        idea_set_tree['flat'] = total_linear_cost
        idea_set_tree['base'] = base_cost
        idea_set_tree['early'] = early_cost
        idea_set_tree['ratio'] = max_ratio
        idea_set_tree['final'] = final_cost
        idea_set_tree['unaccounted'] = unaccounted_string

        result_tree[idea_set_name] = idea_set_tree

result += '|}\n'
print(result)

outfile = open('out/idea_costs.txt', mode = 'w')
outfile.write(str(result_tree))
outfile.close()
