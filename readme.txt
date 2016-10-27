Requires: 
* Unicode-default Python. This includes the default CPython 3, IronPython, and probably Jython, but NOT the default CPython 2.
* pyradox.worldmap requires PIL (or Pillow).

Some scripts are in /scripts/<gamename>. Make sure they actually run before using them as a base, though, I tend to break things after a while.

Module summary:

The most important modules:
pyradox.config: Edit to point to your game directories. Use pyradox.config.setDefaultGame() to set a particular game for a script.
pyradox.struct: Defines the pyradox.struct.Tree class as well as a pyradox.struct.List class. You'll probably want to read this.
pyradox.txt: Parses Paradox .txt files and puts them into a pyradox.struct.Tree which combines aspects of dicts and ElementTrees. Only the three functions at the top are necessary to know for practical use; the rest is the parser itself.

Other modules:
pyradox.format: Some simple string formatting helpers.
pyradox.image: Some simple image processing helpers.
pyradox.primitive: Some helper functions for managing primitives, as well as a pyradox.primitive.Date and pyradox.primitive.Duration class.
pyradox.worldmap: Used for drawing on world maps. Requires PIL. Not the cleanest code, use at your own risk. Might clean it up later.
pyradox.yml: YML localization.
