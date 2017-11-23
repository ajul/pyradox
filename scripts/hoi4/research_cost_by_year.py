import _initpath
import re
import os
import pyradox.hoi4.tech
import pyradox.primitive
import pyradox.struct

import numpy
import matplotlib.pyplot as plt

years = [0] + list(range(1936, 1951, 1))
researchDays = numpy.zeros_like(years)

techs = pyradox.hoi4.tech.getTechs()["technologies"]
for techKey, tech in techs.items():
    if not isinstance(tech, pyradox.struct.Tree): continue
    if 'start_year' not in tech: continue
    startYear = tech['start_year']
    if startYear < years[1]:
        startYear = 0
    yearIndex = years.index(startYear)
    researchDays[yearIndex] += tech['research_cost']


figsize = (16, 9)
dpi = 120
barWidth = 0.8

fig = plt.figure(figsize=figsize)
ax = plt.subplot(111)

x = numpy.arange(len(years))
bars = ax.bar(x - barWidth / 2, researchDays, barWidth, color = 'b')

ax.set_xlabel('Year')
ax.set_ylabel('Total research cost')
ax.set_xticks(x)
ax.set_xticklabels(['Pre-%d' % years[1]] + ['%d' % year for year in years[1:]])

plt.savefig("out/research_cost_by_year.png", dpi = dpi, bbox_inches = "tight")
