import os

import pyradox

parse_provinces, get_provinces = pyradox.load.load_functions('HoI3', 'provinces', ('history', 'provinces'), mode = "walk")
