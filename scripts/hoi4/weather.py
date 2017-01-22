import _initpath
import csv
import os
import re
import collections
import pyradox.config
import pyradox.format
import pyradox.image
import pyradox.wiki
import pyradox.txt

staticModifiers = pyradox.txt.parseFile(os.path.join(pyradox.config.getBasedir('HoI4'), 'common', 'static_modifiers.txt'))

def computeName(k, v):
    return pyradox.format.humanString(k.replace('weather_', ''), capFirst = True)

def isPrecipitation(k, v):
    return 'weather' in k and 'air_accidents' in v

def isTemperature(k, v):
    return 'cold' in k or 'hot' in k

def isGroundEffect(k, v):
    return 'mud' in k or 'ground_snow' in k

def isWeather(k, v):
    return 'weather' in k or k == 'night'

allcolumns = (
    ('Condition', computeName),
    ('Attrition', lambda k, v: pyradox.wiki.coloredPercentString(v['attrition'], color = 'red'), None),
    ('Winter attrition', lambda k, v: pyradox.wiki.coloredPercentString(v['winter_attrition'], color = 'red'), None),
    ('Land speed', lambda k, v: pyradox.wiki.coloredPercentString(v['army_speed_factor'], color = 'red'), None),
    ('Recovery rate', '{{red|%(local_org_regain)0.2f}}', None),
    ('Entrenchment speed', lambda k, v: pyradox.wiki.coloredPercentString(v['dig_in_speed_factor'], color = 'red'), None),
    ('Naval speed', lambda k, v: pyradox.wiki.coloredPercentString(v['naval_speed_factor'], color = 'red'), None),
    ('Naval detection', lambda k, v: pyradox.wiki.coloredPercentString(v['naval_detection'], color = 'red'), None),
    ('Naval hit chance', lambda k, v: pyradox.wiki.coloredPercentString(v['naval_hit_chance'], color = 'red'), None),
    ('Air accidents', lambda k, v: pyradox.wiki.coloredPercentString(v['air_accidents'], color = 'red'), None),
    ('Air detection', lambda k, v: pyradox.wiki.coloredPercentString(v['air_detection'], color = 'red'), None),
    ('Bombing targeting', lambda k, v: pyradox.wiki.coloredPercentString(v['air_bombing_targetting'], color = 'red'), None),
    ('Naval strike', lambda k, v: pyradox.wiki.coloredPercentString(v['naval_strike'], color = 'red'), None),
    )

precipitationColumns = (
    ('Condition', computeName),
    ('Recovery rate', '{{red|%(local_org_regain)0.2f}}', None),
    ('Naval speed', lambda k, v: pyradox.wiki.coloredPercentString(v['naval_speed_factor'], color = 'red'), None),
    ('Naval detection', lambda k, v: pyradox.wiki.coloredPercentString(v['naval_detection'], color = 'red'), None),
    ('Naval hit chance', lambda k, v: pyradox.wiki.coloredPercentString(v['naval_hit_chance'], color = 'red'), None),
    ('Air accidents', lambda k, v: pyradox.wiki.coloredPercentString(v['air_accidents'], color = 'red'), None),
    ('Air detection', lambda k, v: pyradox.wiki.coloredPercentString(v['air_detection'], color = 'red'), None),
    ('Bombing targeting', lambda k, v: pyradox.wiki.coloredPercentString(v['air_bombing_targetting'], color = 'red'), None),
    ('Carrier aircraft can take off', lambda k, v: '{{red|No}}' if 'carrier_traffic' in v else '', None),
    ('Naval strike efficiency', lambda k, v: pyradox.wiki.coloredPercentString(v['naval_strike'], color = 'red'), None),
    )

temperatureColumns = (
    ('Condition', computeName),
    ('Attrition', lambda k, v: pyradox.wiki.coloredPercentString(v['attrition'], color = 'red'), None),
    ('Winter attrition', lambda k, v: pyradox.wiki.coloredPercentString(v['winter_attrition'], color = 'red'), None),
    ('Recovery rate', '{{red|%(local_org_regain)0.2f}}', None),
    ('Entrenchment speed', lambda k, v: pyradox.wiki.coloredPercentString(v['dig_in_speed_factor'], color = 'red'), None),
    )

groundEffectColumns = (
    ('Condition', computeName),
    ('Attrition', lambda k, v: pyradox.wiki.coloredPercentString(v['attrition'], color = 'red'), None),
    ('Land speed', lambda k, v: pyradox.wiki.coloredPercentString(v['army_speed_factor'], color = 'red'), None),
    ('Recovery rate', '{{red|%(local_org_regain)0.2f}}', None),
    )

file = open("out/weather.txt", "w")

file.write(pyradox.wiki.makeWikitable(staticModifiers, precipitationColumns, filterFunction = isPrecipitation))

file.write(pyradox.wiki.makeWikitable(staticModifiers, temperatureColumns, filterFunction = isTemperature))

file.write(pyradox.wiki.makeWikitable(staticModifiers, groundEffectColumns, filterFunction = isGroundEffect))
file.close()
