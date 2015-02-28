import _initpath
import pyradox.csv

countries = {}

for row in pyradox.csv.parseFile('D:/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/config/world_names.csv'):
    countries[row[0].lower()] = row[1]

for row in pyradox.csv.parseFile('D:/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/config/Boostertext.csv'):
    countries[row[0].lower()] = row[1]

result = '{|class = "wikitable sortable"\n'
result += '! Name !! Country !! Skill !! Start year !! End year !! Specialties \n'

count = 0

for filename, table in pyradox.csv.parseDir('D:/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/db/tech/teams'):
    print(table.toTree())
    countryTag = table.getHeaders()[0]
    print(countryTag)
    for row in table:
        if len(row[table.getHeaderIndex('Name')]) == 0: continue
        result += '|-\n'
        result += '| %s ' % row[table.getHeaderIndex('Name')]
        result += '|| %s ' % countries[countryTag]
        result += '|| %s ' % row[table.getHeaderIndex('Skill')]
        result += '|| %s ' % row[table.getHeaderIndex('Start Year')]
        result += '|| %s ' % row[table.getHeaderIndex('End Year')]
        result += '|| '
        i = table.getHeaderIndex('Speciality1')
        while len(row[i]) > 0:
            result += '%s, ' % row[i]
            i = i + 1
        result = result[:-2]
        result += '\n'
        count += 1
        
result += '|}\n'

print(result)

print(count)

