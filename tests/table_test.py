import _initpath
import pyradox.csv

spec = (
    ('Name', '%(name)s'),
    ('Skill', '%(skill)s'),
    ('Start year', '%(start year)s'),
    )

for filename, table in pyradox.csv.parseDir('D:/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/db/tech/teams'):
    print(filename, table.toHTML(spec), table.toWiki(spec))
    
