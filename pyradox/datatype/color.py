import pyradox.image
from pyradox.error import *

import warnings

class Color():
    """
    Represents a color.
    Available colorspaces: hsv (channel values 0.0-1.0) and rgb (channel values 0-255)
    """
    
    COLORSPACES = ['hsv', 'rgb']
    
    COLORSPACE_DATA_TYPES = {
        'hsv' : float,
        'rgb'  : int,
    }
    
    CHANNEL_NAMES = [
        'hue',
        'saturation',
        'value',
        'red',
        'green',
        'blue',
    ]
    
    def __init__(self, channels, colorspace):
        """
        channels: a tuple
        colorspace: hsv or rgb
        """
        colorspace = colorspace.lower()
        if colorspace not in self.COLORSPACES:
            raise ValueError('Colorspace must be one of %s.' % self.COLORSPACES)
        self.colorspace = colorspace
        datatype = self.COLORSPACE_DATA_TYPES[colorspace]
        self.channels = [datatype(c) for c in channels]
        if self.channels != channels:
            warnings.warn(ValueWarning("Loss of precision when converting to canonical datatype for colorspace %s." % colorspace))
        
    def __getitem__(self, index):
        return self.channels[index]
        
    def __getattr__(self, channel_name):
        """
        Get channel by name/letter.
        """
        channel_name = channel_name.lower()
        if channel_name in self.CHANNEL_NAMES: 
            channel_letter = channel_name[0]
        elif len(channel_name) == 1:
            channel_letter = channel_name
        else:
            raise AttributeError()
            
        if channel_letter not in self.channels: raise AttributeError()
        
        return self[self.colorspace.index(channel_letter)]
        
    def __str__(self):
        if self.COLORSPACE_DATA_TYPES[self.colorspace] is int:
            return '%s { %d %d %d }' % ((self.colorspace,) + tuple(self.channels))
        else:
            return '%s { %0.2f %0.2f %0.2f }' % ((self.colorspace,) + tuple(self.channels))

    def __iter__(self):
        for x in self.channels: yield x
            
    def to_rgb(self):
        if self.colorspace == 'rgb': 
            return Color(self.channels, 'rgb')
        elif self.colorspace == 'hsv':
            channels = pyradox.image.HSVtoRGB(self.channels)
            return Color(channels, 'rgb')