import _initpath
import pyradox.csv

spec = (
    ('Name', '%(name)s'),
    ('Skill', '%(skill)s'),
    ('Start year', '%(start year)s'),
    )

for filename, table in pyradox.csv.parse_dir('D:/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/db/tech/teams'):
    print(filename, table.to_html(spec), table.to_wiki(spec))
    
