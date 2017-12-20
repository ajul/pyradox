import _initpath
import pyradox.csv

countries = {}

for row in pyradox.csv.parse_file('D:/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/config/world_names.csv'):
    countries[row[0].lower()] = row[1]

for row in pyradox.csv.parse_file('D:/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/config/Boostertext.csv'):
    countries[row[0].lower()] = row[1]

result = '{|class = "wikitable sortable"\n'
result += '! Name !! Country !! Skill !! Start year !! End year !! Specialties \n'

count = 0

for filename, table in pyradox.csv.parse_dir('D:/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/db/tech/teams'):
    print(table.to_tree())
    country_tag = table.get_headers()[0]
    print(country_tag)
    for row in table:
        if len(row[table.get_header_index('Name')]) == 0: continue
        result += '|-\n'
        result += '| %s ' % row[table.get_header_index('Name')]
        result += '|| %s ' % countries[country_tag]
        result += '|| %s ' % row[table.get_header_index('Skill')]
        result += '|| %s ' % row[table.get_header_index('Start Year')]
        result += '|| %s ' % row[table.get_header_index('End Year')]
        result += '|| '
        i = table.get_header_index('Speciality1')
        while len(row[i]) > 0:
            result += '%s, ' % row[i]
            i = i + 1
        result = result[:-2]
        result += '\n'
        count += 1
        
result += '|}\n'

print(result)

print(count)

