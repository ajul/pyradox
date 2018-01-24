from PIL import Image

def linear_to_srgb(x):
    # using floats, returns int
    def component(c):
        if c <= 0.0031308:
            return 12.92 * c
        else:
            return 1.055 * pow(c, 1/2.4) - 0.055
    return tuple(int(round(component(c) * 255.0)) for c in x)
    
def HSVtoRGB(pixel):
    # inputs floats, outputs 0-255
    h = pixel[0]
    s = pixel[1]
    v = pixel[2]
    
    c = v * s
    h = h * 6
    x = c * (1 - abs(h % 2.0 - 1))
    
    if h < 1.0:   r, g, b = c, x, 0
    elif h < 2.0: r, g, b = x, c, 0
    elif h < 3.0: r, g, b = 0, c, x
    elif h < 4.0: r, g, b = 0, x, c
    elif h < 5.0: r, g, b = x, 0, c
    else:         r, g, b = c, 0, x
    
    m = v - c
    
    r += m
    g += m
    b += m
    
    r = int(round(r * 255.0))
    g = int(round(g * 255.0))
    b = int(round(b * 255.0))
    
    return (r, g, b)

def colormap_blue_red(x):
    """Given x between 0 and 1, interpolates between blue and red."""
    return linear_to_srgb((x, 0.0, 1.0 - x))

def colormap_red_green(x):
    """Given x between 0 and 1, interpolates between red and green."""
    return linear_to_srgb((1.0 - x, x, 0.0))

def get_strip_square(image, idx):
    """gets the idxth square from a horizontal strip of images"""
    square_size = image.size[1]
    x_start = square_size * idx
    result = image.crop((x_start, 0, x_start + square_size, square_size))
    result.load()
    return result

def split_strip(image, subwidth = None):
    """gets a list of subimages from a horizontal strip of images"""
    if subwidth is None:
        subwidth = image.size[1]
    result = []
    for x_start in range(0, image.size[0], subwidth):
        sub_image = image.crop((x_start, 0, x_start + subwidth, subwidth))
        sub_image.load()
        result.append(sub_image)
    return result

def save_using_palette(image, filename, colors = 256):
    """save image using palette and optimization"""
    image.convert("P", dither = Image.NONE, palette = Image.ADAPTIVE, colors = colors).save(filename, optimize = True)
