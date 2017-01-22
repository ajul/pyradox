import _initpath

from PIL import Image
import pyradox.config
import os

flagdir = os.path.join(pyradox.config.getBasedir('HoI4'), 'gfx', 'flags')

for filename in os.listdir(flagdir):
    fullpath = os.path.join(flagdir, filename)
    basename, ext = os.path.splitext(filename)
    if ext != '.tga': continue

    print(basename)
    image = Image.open(fullpath)
    image.save(os.path.join('out', 'flags', basename + '.png'))
