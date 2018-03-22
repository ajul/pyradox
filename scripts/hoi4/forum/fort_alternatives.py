import numpy
import matplotlib.pyplot as plt

dpi = 64
figsize = (12, 8)

lin_scale = 0.15
geo_scale = 0.8
inv_scale = 1.0

offset = 0.0

x = numpy.arange(0.0, 11.0)

m_lin = 1.0 - 0.15 * x
m_geo = numpy.power(geo_scale, x)
m_inv = 1.0 / (1.0 + inv_scale * x)

def compute_y(m, offset = 0.0):
    return 1.0 / numpy.maximum(m + offset, 0.01)

fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
ax.plot(x, compute_y(m_lin, offset), fillstyle='full', marker='^', linestyle='-', color = 'red')
ax.plot(x, compute_y(m_geo, offset), fillstyle='full', marker='>', linestyle='-', color = 'green')
ax.plot(x, compute_y(m_inv, offset), fillstyle='full', marker='v', linestyle='-', color = 'blue')

ax.legend(
    [
        'Linear penalty ({:.1f}% per level)'.format(lin_scale * 100.0),
        'Geometric penalty (x{:.1f} per level)'.format(geo_scale),
        'Inverse linear penalty ({:.1f}% per level)'.format(inv_scale * 100.0),
        ],
    loc = 'upper left',
    )

ax.set_title('Fort effects (attacker fort bonus {:0.1f}%)'.format(offset * 100.0))
ax.set_xlabel('Fort level')
ax.set_ylabel('Defender survivability')
ax.set_ylim(bottom = 0.0, top = 11.0)
plt.tight_layout()
plt.savefig('fort_alternatives_{:0.1f}.png'.format(offset))
plt.show()
