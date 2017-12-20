import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy

x_min = 40.0
x_step = 20.0
x_max = 300.0

# pop per year at start
starting_pop_per_year = numpy.linspace(x_min, x_max, 1001)
xticks = numpy.arange(0.0, x_max + x_step * 0.5, x_step)


starting_pop_per_month = starting_pop_per_year / 12.0
required_time = numpy.zeros_like(starting_pop_per_month)
for i in range(10):
    #level = max(i - 1, 0)
    level_pop_per_month = i # level * 4% per level * 3 per year per level / 12 months per year
    curr_rate = starting_pop_per_month + level_pop_per_month
    required_time += 100.0 / curr_rate

ymax = (numpy.max(required_time) // 12 + 1) * 12.0
yticks = numpy.arange(0.0, ymax + 18.0, 12.0)

plt.plot(starting_pop_per_year, required_time)
plt.xlabel('Starting growth per year (flat + chance * 3)')
plt.xticks(xticks)
plt.yticks(yticks)
plt.ylabel('Months to city')
plt.xlim(xmin=x_min)
plt.ylim(ymin=0, ymax = ymax)
plt.grid(True)
plt.show()



