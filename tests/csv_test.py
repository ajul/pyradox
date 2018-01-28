import _initpath
import pyradox.filetype.csv
import pyradox.filetype.table

spec = (
    ('Name', '%(name)s'),
    ('Skill', '%(skill)s'),
    ('Start year', '%(start year)s'),
    )

for filename, tree in pyradox.filetype.csv.parse_dir('C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron 2 Complete Pack/Doomsday/db/tech/teams'):
    print(pyradox.filetype.table.make_table(tree, 'wiki'))
    
