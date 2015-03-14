import _initpath
import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml
import pyradox.eu4.country

ideaMap = pyradox.txt.parseFile('out/idea_map.txt')
ideaCosts = pyradox.txt.parseFile('out/idea_costs.txt')
nonIdeaCosts = pyradox.txt.parseFile('out/non_idea_costs.txt')

result = '{|class = "wikitable sortable"\n'
result += '! Country !! Tag !! Territory cost !! Ruler cost !! Government cost !! Technology cost '
result += '!! Idea cost (without ratio) !! Idea cost (with ratio) !! Total cost (without ratio) !! Total cost (with ratio) \n'

for tag, ideaGroupName in ideaMap.items():
    territoryCost = nonIdeaCosts[tag]['territory']
    if territoryCost == 0: continue
    earlyCost = ideaCosts[ideaGroupName]['early']
    finalCost = ideaCosts[ideaGroupName]['final']
    
    rulerCost = nonIdeaCosts[tag]['ruler']
    governmentCost = nonIdeaCosts[tag]['government']
    technologyCost = nonIdeaCosts[tag]['technology']

    totalEarlyCost = territoryCost + rulerCost + governmentCost + technologyCost + earlyCost
    totalFinalCost = territoryCost + rulerCost + governmentCost + technologyCost + finalCost
    
    result += '|-\n'

    result += '| %s || %s || %d || %0.1f || %d || %d ' % (
        pyradox.eu4.country.getCountryName(tag), tag, territoryCost,
        rulerCost, governmentCost, technologyCost)

    result += '|| %0.1f || %0.1f || %0.1f || %0.1f \n' % (
        earlyCost, finalCost, totalEarlyCost, totalFinalCost,
        )

result += '|}\n'

print(result)
