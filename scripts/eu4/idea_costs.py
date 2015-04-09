import _initpath
import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml

import ideaoptions

def cost0_3(level):
    return 3 * (level - 1) * level / 2

def cost0_5(level):
    return 5 * (level - 1) * level / 2

costFunctions = {
    (0, 3) : cost0_3,
    (0, 5) : cost0_5,
    (0, 15) : lambda level: cost0_5(level * 2 - 1),
    (3, 18) : lambda level: cost0_3(level * 2),
    (5, 30) : lambda level: cost0_5(level * 2),
    (15, 50) : lambda level: cost0_5(level * 2 + 1),
    (30, 140) : lambda level: cost0_5(level * 4),
}

bonuses = {}

def evalBonus(bonusKey, bonusValue):
    if bonusKey in bonuses:
        powerType, baseValue, max_level, costs = bonuses[bonusKey]
        costFunction = costFunctions[costs]
        level = bonusValue / baseValue
        return powerType, 10 * level / max_level, costFunction(level), costs[0] + (level - 1) * (costs[1] - costs[0])
    else:
        return None

for fileName, fileData in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'custom_ideas')):
    for ideaSet in fileData.values():
        # start category
        
        for idea, ideaData in ideaSet.items():
            if idea == 'category':
                powerType = ideaData.lower()
                continue

            costs = [0, 5] # cost indexed by level (0-based)
            max_level = 4
            for key, value in ideaData.items():
                if key in ('default', 'chance'):
                    continue
                elif key == 'max_level':
                    max_level = value
                elif 'level_cost_' in key:
                    level = int(key[len('level_cost_'):])
                    if level <= 2:
                        costs[level - 1] = value
                else:
                    bonusKey = key
                    baseValue = value
            bonuses[bonusKey] = (powerType, baseValue, max_level, tuple(costs))

result = '{|class = "wikitable sortable"\n'
result += '! Idea group !! Linear cost !! Base cost !! Adjusted for<br/>early ideas !! Max level ratio !! Final cost !! Bonuses unaccounted for\n'

resultTree = pyradox.struct.Tree()

for fileName, fileData in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'ideas')):
    for ideaSetName, ideaSet in fileData.items():
        
        index = 0
        baseCost = 0.0
        earlyCost = 0.0
        totalLinearCost = 0.0
        unaccounted = [] # not appearing in designer
        levelCounts = {
            'adm' : 0.0,
            'dip' : 0.0,
            'mil' : 0.0,
            }
        for key, value in ideaSet.items():
            if key in ('category', 'trigger', 'free', 'ai_will_do', 'important'): continue
            
            if key == 'start':
                costMultiplier = 2
            elif key == 'bonus':
                costMultiplier = 1
            else:
                costMultiplier = 2 - 0.2 * min(index, 5)
                index += 1

            for bonusKey, bonusValue in value.items():
                bonusInfo = evalBonus(bonusKey, bonusValue)
                if bonusInfo is None:
                    unaccounted.append('%s (%s)' %( bonusKey, bonusValue))
                else:
                    powerType, level, cost, linearCost = bonusInfo
                    levelCounts[powerType] += level
                    baseCost += cost
                    earlyCost += cost * costMultiplier
                    totalLinearCost += linearCost

        maxRatio = max(levelCounts.values()) / sum(levelCounts.values())
        finalCost = earlyCost * (1 + 5 * max(0, maxRatio - 0.5))
        unaccountedString = '%d: %s' % (len(unaccounted), ', '.join(unaccounted))
        result += '|-\n'
        result += '| %s || %0.1f || %0.1f || %0.1f || %0.1f%% || %0.1f || %s \n' % (ideaSetName, totalLinearCost, baseCost, earlyCost, maxRatio * 100, finalCost, unaccountedString)

        ideaSetTree = pyradox.struct.Tree()

        ideaSetTree['flat'] = totalLinearCost
        ideaSetTree['base'] = baseCost
        ideaSetTree['early'] = earlyCost
        ideaSetTree['ratio'] = maxRatio
        ideaSetTree['final'] = finalCost
        ideaSetTree['unaccounted'] = unaccountedString

        resultTree[ideaSetName] = ideaSetTree

result += '|}\n'
print(result)

outfile = open('out/idea_costs.txt', mode = 'w')
outfile.write(str(resultTree))
outfile.close()
