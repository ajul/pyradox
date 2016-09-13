import _initpath
import pyradox

#result = pyradox.txt.parseFile('D:/Steam/steamapps/common/Europa Universalis IV/common/prices/00_prices.txt')
#print(result)

result = pyradox.parse("""
# pre comment
foo = bar # line comment

1 # pre comment
= # pre comment
3 # line comment

# tree test
tree = {
# pre comment in tree
foo = bar # line comment in tree
# tree end comment
} # line comment

# list test
list = {
# pre comment in list
foo # line comment in list
# list end comment
} # line comment
# file end comment

list2 = {1 2 3}
""")

print(result)
