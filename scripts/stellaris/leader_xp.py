xp_base = 200
xp_increment = 75

max_level = 10

levels = [x for x in range(1, max_level + 1)]

xp_from_last = xp_base
xp_total = 0

leader_types = [
    ('Ruler', 5.0),
    ('Research scientist<br/>Idle governor', 3.5),
    ]

xp = []
for level in levels:
    xp.append(xp_total)
    xp_total += xp_from_last
    xp_from_last += xp_increment

result = '{|class = "wikitable"  style="text-align:right;"\n'
result += '! Level !! '
result += ' || '.join(str(x) for x in levels)
result += '\n|-\n'
result += '! XP \n| '
result += ' || '.join(str(x) for x in xp)

for name, xp_per_month in leader_types:
    result += '\n|-\n'
    result += '! %s \n| ' % name
    result += ' || '.join('%0.1f years' % (x / xp_per_month / 12) for x in xp)

result += '\n|}\n'

print(result)
