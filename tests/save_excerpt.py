# import _initpath
import re
import sys
import pyradox.primitive
import pyradox.table
import pyradox.txt

landUnits = [
    'infantry',
    'cavalry',
    'artillery',
    ]

navalUnits = [
    'heavy_ship',
    'light_ship',
    'galley',
    'transport',
    ]

allUnits = landUnits + navalUnits

unitHeadings = [side + '_' + unit for unit in allUnits for side in ('attacker', 'defender')]

headings = [
    'war_name', 'battle_name',
    'year', 'month', 'day',
    'war_attacker', 'war_defender',
    'attacker', 'defender', 'winner',
    'type', # land or naval
    'attacker_commander', 'defender_commander',
    'attacker_losses', 'defender_losses',
    ] + unitHeadings

def extract(inFileName, outFileName):
    # open and read the save
    inFile = open(inFileName)
    data = inFile.read()
    inFile.close()
    m = re.search('((active|previous)_war=.*)(?=income_statistics)', data, flags = re.DOTALL)
    data = pyradox.txt.parse(m.group(1))

    result = pyradox.table.Table(headings)

    for warType, warData in data.items():
        warRow = {
            'war_name' : warData['name'],
            'war_attacker' : warData['original_attacker'],
            'war_defender' : warData['original_defender'],
            }

        for date, events in warData['history'].items():
            if not isinstance(date, pyradox.primitive.Date): continue
            for battleKey, battleData in events.items():
                if battleKey != 'battle': continue
                battleRow = {
                    'battle_name' : battleData['name'],
                    'year' : date.year,
                    'month' : date.month,
                    'day' : date.day,
                    'attacker' : battleData['attacker']['country'],
                    'defender' : battleData['defender']['country'],
                    'winner' : 'attacker' if battleData['result'] else 'defender',
                    'type' : 'naval' if (
                        any(unit in battleData['attacker'].keys() for unit in navalUnits) or
                        any(unit in battleData['defender'].keys() for unit in navalUnits)
                        ) else 'land',
                    'attacker_commander' : battleData['attacker']['commander'],
                    'defender_commander' : battleData['defender']['commander'],
                    'attacker_losses' : battleData['attacker']['losses'],
                    'defender_losses' : battleData['defender']['losses'],
                    }
                for unit in allUnits:
                    for side in ('attacker', 'defender'):
                        battleRow[side + '_' + unit] = battleData[side][unit] if unit in battleData[side] else 0
                battleRow.update(warRow)
                result.addRow(battleRow)

    outFile = open(outFileName, mode='w')
    outFile.write(result.toCSV(separator=','))
    outFile.close()

