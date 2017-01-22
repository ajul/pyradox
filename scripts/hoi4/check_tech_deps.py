import _initpath
import os
import pyradox.hoi4.tech
import pyradox.primitive
import pyradox.struct

techs = pyradox.hoi4.tech.getTechs()["technologies"]

# child tech -> [parentTech, ...]
techsOrDependencies = {}

for techKey, tech in techs.items():
    if isinstance(tech, pyradox.struct.Tree):
        for path in tech.findAll('path'):
            childTechKey = path['leads_to_tech']
            if childTechKey not in techsOrDependencies:
                techsOrDependencies[childTechKey] = []
            techsOrDependencies[childTechKey].append(techKey)

def checkDeps(techKeys, filename, date):
    for techKey in techKeys:
        tech = techs[techKey]
        if 'xor' in tech:
            for otherTechKey in tech['xor']:
                if otherTechKey in techKeys:
                    print('%s : %s : Tech %s violates mutual exclusivity with: %s' % (filename, date, techKey, otherTechKey))
        if 'dependencies' in tech:
            for otherTechKey in tech['dependencies']:
                if otherTechKey not in techKeys:
                    print('%s : %s : Tech %s is missing prerequisite: %s' % (filename, date, techKey, otherTechKey))

        if techKey in techsOrDependencies:
            ancestors = list(techsOrDependencies[techKey])
            researchedAncestors = []
            while len(ancestors) > 0:
                ancestor = ancestors.pop()
                if ancestor in techKeys:
                    # found root tech
                    if ancestor not in techsOrDependencies: break
                    # otherwise dig further
                    researchedAncestors.append(ancestor)
                    ancestors += list(techsOrDependencies[ancestor])
            else:
                printString = '%s : %s : Tech %s is missing prerequsite' % (filename, date, techKey)
                if len(researchedAncestors) > 0:
                    printString += ' via: '
                    for otherTechKey in researchedAncestors:
                        printString += otherTechKey + ', '
                    printString = printString[:-2] + '.'
                else:
                    printString += ', needs one of: '
                    for otherTechKey in techsOrDependencies[techKey]:
                        printString += otherTechKey + ', '
                    printString = printString[:-2] + '.'
                print(printString)

def checkYears(techKeys, filename, date):
    for techKey in techKeys:
        tech = techs[techKey]
        if (tech['start_year'] or 0) > date.year:
            print('%s : %s : Tech %s is ahead of time with year %s' % (filename, date, techKey, tech['start_year']))

for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    techKeys = set(country['set_technology'].keys())
    checkDeps(techKeys, filename, pyradox.primitive.Date('1936.1.1'))
    for date, effects in country.items():
        if not isinstance(date, pyradox.primitive.Date): continue
        if 'set_technology' not in effects: continue
        techKeys |= set(effects['set_technology'].keys())
        checkDeps(techKeys, filename, date)

for filename, country in pyradox.txt.parseDir(os.path.join(pyradox.config.getBasedir('HoI4'), 'history', 'countries')):
    techKeys = set(country['set_technology'].keys())
    checkYears(techKeys, filename, pyradox.primitive.Date('1936.1.1'))
    for date, effects in country.items():
        if not isinstance(date, pyradox.primitive.Date): continue
        if 'set_technology' not in effects: continue
        techKeys |= set(effects['set_technology'].keys())
        checkYears(techKeys, filename, date)
