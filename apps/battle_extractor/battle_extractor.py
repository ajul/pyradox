import traceback

import io
import re
import os
import sys
import zipfile

sys.path.append("../..")
import pyradox.primitive
import pyradox.table
import pyradox.txt

warHeadings = [
    'war_name',
    'start_year', 'start_month', 'start_day',
    'end_year', 'end_month', 'end_day',
    'number_of_battles',
    'country', 'side', 'is_war_leader',
    'friendly_losses', 'enemy_losses',
    ]

battleHeadings = [
    'war_name', 'battle_name',
    'year', 'month', 'day',
    'country', 'enemy', 'side', 'won',
    'type', # land or naval
    'friendly_leader', 'enemy_leader',
    'friendly_strength', 'enemy_strength',
    'friendly_losses', 'enemy_losses',
    ]

shipWords = ['ship', 'transport', 'galley', 'commerce_raider', 'cruiser', 'dreadnought', 'frigate', 'ironclad', 'man_o_war', 'monitor']

def isNaval(battleData):
    for key in (battleData['attacker'] + battleData['defender']).keys():
        if any(word in key for word in shipWords): return True
    return False

def findBelligerents(warData):
    # return country, side, is_war_leader
    foundAttackerWarLeader = False
    foundDefenderWarLeader = False

    for date, events in warData['history'].items():
        if not isinstance(date, pyradox.primitive.Date): continue
        for key, value in events.items():
            if key == 'add_attacker':
                yield value, 'attacker', not foundAttackerWarLeader
                foundAttackerWarLeader = True
            elif key == 'add_defender':
                yield value, 'defender', not foundDefenderWarLeader
                foundDefenderWarLeader = True

def findWarStartDate(warData):
    for date, events in warData['history'].items():
        if isinstance(date, pyradox.primitive.Date): return date

def findWarEndDate(warData):
    for date in reversed([x for x in warData['history'].keys()]):
        if isinstance(date, pyradox.primitive.Date): return date

def findStrength(sideData):
    return sum(value for key, value in sideData.items() if isinstance(value, int) and key not in ('losses',))

def processBattle(battleTable, warLosses, warName, date, battleData):
    if date is None:
        year, month, day = '', '', ''
    else:
        year, month, day = date.year, date.month, date.day

    attackerData = battleData['attacker']
    defenderData = battleData['defender']

    warLosses[0] += attackerData['losses']
    warLosses[1] += defenderData['losses']

    battleTable.addRow({
        'war_name' : warName,
        'battle_name' : battleData['name'] or '',
        'year' : year,
        'month' : month,
        'day' : day,
        'country' : attackerData['country'] or '',
        'enemy' : defenderData['country'] or '',
        'side' : 'attacker',
        'won' : battleData['result'],
        'type' : 'naval' if isNaval(battleData) else 'land', # land or naval
        'friendly_leader' : attackerData['commander'] or attackerData['leader'] or '',
        'enemy_leader' : defenderData['commander'] or defenderData['leader'] or '',
        'friendly_strength' : findStrength(attackerData),
        'enemy_strength' : findStrength(defenderData),
        'friendly_losses' : attackerData['losses'],
        'enemy_losses' : defenderData['losses'],
    })

    battleTable.addRow({
        'war_name' : warName,
        'battle_name' : battleData['name'] or '',
        'year' : year,
        'month' : month,
        'day' : day,
        'country' : defenderData['country'] or '',
        'enemy' : attackerData['country'] or '',
        'side' : 'defender',
        'won' : not battleData['result'],
        'type' : 'naval' if isNaval(battleData) else 'land', # land or naval
        'friendly_leader' : defenderData['commander'] or defenderData['leader'] or '', 
        'enemy_leader' : attackerData['commander'] or attackerData['leader'] or '',
        'friendly_strength' : findStrength(defenderData),
        'enemy_strength' : findStrength(attackerData),
        'friendly_losses' : defenderData['losses'],
        'enemy_losses' : attackerData['losses'],
    })

def extract(inFilename, outFilenameBase = None):
    if outFilenameBase is None:
        outFilenameBase = inFileName
    
    # open and read the save
    if zipfile.is_zipfile(inFilename):
        inFile = zipfile.ZipFile(inFilename)
        for info in inFile.infolist():
            if info.filename != 'meta':
                data = inFile.read(info).decode(pyradox.txt.encoding)
        inFile.close()
    else:
        inFile = open(inFilename, encoding=pyradox.txt.encoding)
        data = inFile.read()
        inFile.close()
    m = re.search('(^(active|previous)_war\s*=.*?)^(?=\w+)(?!(active|previous)_war)', data, flags = re.DOTALL | re.MULTILINE)
    if m is None:
        raise Exception("War data not found.")

    data = pyradox.txt.parse(m.group(1), filename=inFilename)

    warTable = pyradox.table.Table(warHeadings)
    battleTable = pyradox.table.Table(battleHeadings)

    for warType, warData in data.items():
        warName = warData['name']

        startDate = findWarStartDate(warData)
        if startDate is None:
            startYear, startMonth, startDay = '', '', ''
        else:
            startYear, startMonth, startDay = startDate.year, startDate.month, startDate.day
        if warType == 'active_war':
            endYear = 'present'
            endMonth = 'present'
            endDay = 'present'
        else:
            endDate = findWarEndDate(warData)
            if endDate is None:
                endYear, endMonth, endDay = '', '', ''
            else:
                endYear, endMonth, endDay = endDate.year, endDate.month, endDate.day

        warLosses = [0, 0]
        numBattles = 0

        for date, events in warData['history'].items():
            if isinstance(date, pyradox.primitive.Date):
                for eventType, battleData in events.items():
                    if eventType == 'battle':
                        processBattle(battleTable, warLosses, warName, date, battleData)
                        numBattles += 1
            else:
                if date == 'battle':
                    processBattle(battleTable, warLosses, warName, startDate, events)
                    numBattles += 1

        for country, side, isWarLeader in findBelligerents(warData):
            warTable.addRow({
                'war_name' : warName,
                'start_year' : startYear,
                'start_month' : startMonth,
                'start_day' : startDay,
                'end_year' : endYear,
                'end_month' : endMonth,
                'end_day' : endDay,
                'number_of_battles' : numBattles,
                'country' : country,
                'side' : side,
                'is_war_leader' : isWarLeader,
                'friendly_losses' : warLosses[0] if side == 'attacker' else warLosses[1],
                'enemy_losses' : warLosses[0] if side == 'defender' else warLosses[1],
                })

    outWarFile = open(outFilenameBase + '.war.csv', mode='w', encoding=pyradox.txt.encoding)
    outWarFile.write(warTable.toCSV(separator=','))
    outWarFile.close()

    outBattleFile = open(outFilenameBase + '.battle.csv', mode='w', encoding=pyradox.txt.encoding)
    outBattleFile.write(battleTable.toCSV(separator=','))
    outBattleFile.close()

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        # explicit input and output files
        extract(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        # put output file at same place as input
        extract(sys.argv[1])
    else:
        # use in/ and out/ dirs
        dirname = 'in'
        for filename in os.listdir(dirname):
            inFilename = os.path.join(dirname, filename)
            outFilenameBase = os.path.join('out', filename)
            if os.path.isfile(inFilename):
                try:
                    extract(inFilename, outFilenameBase)
                except:
                    print('Failed to extract data from %s.' % inFilename)
                    traceback.print_exc()
                else:
                    print('Extracted data from %s and written to %s.' % (inFilename, outFilenameBase))
                
                
