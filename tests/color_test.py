import _initpath
import pyradox

import re

result = pyradox.parse(r"""
r = rgb { 1 100 200 }
h = hsv { 0.3 0.6 0.9 }
""")

print(result)
