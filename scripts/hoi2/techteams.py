import _initpath

"""
countries = {}

for row in pyradox.csv.parse_file('C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/config/world_names.csv'):
    countries[row[0].lower()] = row['english']

for row in pyradox.csv.parse_file('C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/config/Boostertext.csv'):
    countries[row[0].lower()] = row['english']
"""

result = '{|class = "wikitable sortable"\n'
result += '! Name !! Country !! Skill !! Start year !! End year !! Specialties \n'

count = 0

for filename, table in pyradox.csv.parse_dir('C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/db/tech/teams'):
    print(table.to_tree('name'))
    country_tag = table.get_headings()[0]
    print(country_tag)
    for row in table:
        if len(row['name']) == 0: continue
        result += '|-\n'
        result += '| %s ' % row['name']
        result += '|| %s ' % country_tag
        result += '|| %s ' % row['skill']
        result += '|| %s ' % row['start year']
        result += '|| %s ' % row['end year']
        result += '|| '

        for i in range(1, 33):
            key = 'speciality%d' % i
            if key not in row: break
            if len(row[key]) == 0: break
            result += '%s, ' % row[key]
            
        result = result[:-2]
        result += '\n'
        count += 1
        
result += '|}\n'

print(result)

print(count)

