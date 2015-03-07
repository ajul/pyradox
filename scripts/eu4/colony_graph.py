import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy

xMin = 40.0
xStep = 20.0
xMax = 300.0

# pop per year at start
startingPopPerYear = numpy.linspace(xMin, xMax, 1001)
xticks = numpy.arange(0.0, xMax + xStep * 0.5, xStep)


startingPopPerMonth = startingPopPerYear / 12.0
requiredTime = numpy.zeros_like(startingPopPerMonth)
for i in range(10):
    #level = max(i - 1, 0)
    levelPopPerMonth = i # level * 4% per level * 3 per year per level / 12 months per year
    currRate = startingPopPerMonth + levelPopPerMonth
    requiredTime += 100.0 / currRate

ymax = (numpy.max(requiredTime) // 12 + 1) * 12.0
yticks = numpy.arange(0.0, ymax + 18.0, 12.0)

plt.plot(startingPopPerYear, requiredTime)
plt.xlabel('Starting growth per year (flat + chance * 3)')
plt.xticks(xticks)
plt.yticks(yticks)
plt.ylabel('Months to city')
plt.xlim(xmin=xMin)
plt.ylim(ymin=0, ymax = ymax)
plt.grid(True)
plt.show()



