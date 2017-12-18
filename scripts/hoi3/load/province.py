import os
import pyradox.config
import pyradox.format
import pyradox.load
import pyradox.txt
import pyradox.struct

parseProvinces, getProvinces = pyradox.load.loadFunctions('HoI3', 'provinces', ('history', 'provinces'), mode = "walk")
