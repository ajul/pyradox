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
    if tech['doctrine']: continue
    startYear = tech['start_year'] or 0
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

ax.set_title('Total research cost by tech year (no doctrines)')
ax.set_xlim(-1, len(years))
ax.set_xlabel('Year')
ax.set_ylabel('Total research cost')
ax.set_xticks(x)
ax.set_xticklabels(['Pre-%d' % years[1]] + ['%d' % year for year in years[1:]])

baseline = 5 * 360.0 / 100.0
ax.plot([-1, len(years)], [baseline, baseline],
        color='#7f7f7f', linestyle='-', zorder=0)
plt.text(len(years) - 0.5, baseline, '5 research slots x 360 days, no modifiers',
         fontsize = 12,
         rotation = 0,
         ha = 'right', va = 'bottom');

plt.savefig("out/research_cost_by_year.png", dpi = dpi, bbox_inches = "tight")
