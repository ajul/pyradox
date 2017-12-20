import _initpath
import pyradox

import re

result = pyradox.parse(r"""
random_owned_controlled_state = {
        prioritize = { 43 }
        limit = { ROOT = { has_full_control_of_state = PREV } }
        create_unit = {
                division = "name = \"1. Light Division\" division_template = \"Light Division\" start_experience_factor = 1.0" 
                owner = HUN
        }
}
""")

print(result)
