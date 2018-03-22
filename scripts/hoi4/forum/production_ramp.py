import numpy
import matplotlib.pyplot as plt

dpi = 64
figsize = (12, 8)

x = numpy.linspace(0, 1, 1025)
y = 500 / 3 * (1 + 2 * numpy.power(x, 3) - 3 * numpy.power(x, 2))

fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

ax.plot(x, y, color = 'blue')

ax.set_title('Ramp-up production losses')
ax.set_xlabel('Starting production efficiency / production efficiency cap')
ax.set_ylabel('Factory-days lost during ramp-up')
ax.grid(True)
plt.tight_layout()
plt.savefig('production_ramp.png')
plt.show()
