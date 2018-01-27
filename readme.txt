Requires: 
* Unicode-default Python. This includes the default CPython 3, IronPython, and probably Jython, but NOT the default CPython 2.
* pyradox.worldmap requires PIL (or Pillow).

Some scripts are in /scripts/<gamename>. Make sure they actually run before using them as a base, though, I tend to break things after a while. I suggest looking at recently-edited files.

The most important modules:
pyradox.datatype.tree: The core data structure. Combines aspects of dicts and ElementTrees.
pyradox.filetype.txt: Parses Paradox .txt files and puts them into a pyradox.datatype.Tree. Only the three functions at the top are necessary to know for practical use; the rest is the parser itself.
