import _initpath
import pyradox

#result = pyradox.txt.parse_file('D:/Steam/steamapps/common/Europa Universalis IV/common/prices/00_prices.txt')
#print(result)

result = pyradox.parse("""
regular_group = { 1 2 3 }

empty_tree = {}

mixed_group = {
    10
    {}
    { a = 1 b = 2 }
    20
}

player_countries={
	ITA={
		user="Evil4Zerggin"
		country_leader=yes
		pinned_theatres={
{
				id=16
				type=67
			}
		}
	}
}
""")

print(result)
