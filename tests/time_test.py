import _initpath
import pyradox

import re

result = pyradox.parse(r"""
with_days = 1444.1.1
with_hours = 1939.1.1.12
""")

print(result)

print(pyradox.Time.from_days_since_1_ad(365 + 32))
