import _initpath
import pyradox

#result = pyradox.txt.parse_file('D:/Steam/steamapps/common/Europa Universalis IV/common/prices/00_prices.txt')
#print(result)

result = pyradox.parse("""
# pre comment
foo = bar # line comment 0

1 # pre comment
= # pre comment
3 # line comment

empty_tree = {}

# tree test
tree = {
# pre comment in tree
foo = bar # line comment in tree
# tree end comment
} # tree line comment

# group outside precomment?
group = {
    # group item precomment
    foo # line comment in group
    bar baz
    # group item postcomment
} # group outside postcomment?

list2 = {1 2 3}

# file end comment (or item outside postcomment?)
""")

print(result)
