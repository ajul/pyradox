import numpy
import matplotlib.pyplot as plt

x02 = numpy.arange(0.0, 1.17, 0.01)
x01 = numpy.arange(0.0, 1.34, 0.01)
x11 = numpy.arange(0.0, 1.34, 0.01)

y02 = numpy.minimum(x02, x02 * (3.0 - 2.0 * x02))
y01 = numpy.minimum(x01, x01 * (2.0 - 1.0 * x01))
y11 = x11 * (2.0 - 1.0 * x01)

plt.figure(figsize=(9, 15), dpi=64)
plt.subplot(3, 1, 1)
plt.plot(x02 * 100.0, y02 * 100.0)
plt.xlim([0.0, 133.0])
plt.ylim([0.0, 110.0])
plt.title('-2% per % over width (current)')
plt.ylabel('Effective attack %')

plt.subplot(3, 1, 2)
plt.plot(x01 * 100.0, y01 * 100.0)
plt.xlim([0.0, 133.0])
plt.ylim([0.0, 110.0])
plt.title('-1% per % over width (original proposal)')
plt.ylabel('Effective attack %')

plt.subplot(3, 1, 3)
plt.plot(x11 * 100.0, y11 * 100.0)
plt.xlim([0.0, 133.0])
plt.ylim([0.0, 110.0])
plt.title('-1% per % over width, +1% per % under width')
plt.ylabel('Effective attack %')

plt.xlabel('Width %')

plt.savefig('width_penalty.png')
plt.show()
