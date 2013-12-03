def linearTosRGB(x):
    # using floats, returns int
    def component(c):
        if c <= 0.0031308:
            return 12.92 * c
        else:
            return 1.055 * pow(c, 1/2.4) - 0.055
    return tuple(round(component(c) * 255.0) for c in x)

def colormapBlueRed(x):
    """Given x between 0 and 1, interpolates between blue and red."""
    return linearTosRGB((x, 0.0, 1.0 - x))

def getStripSquare(image, idx):
    """gets the idxth square from a horizontal strip of images"""
    squareSize = image.size[1]
    xStart = squareSize * idx
    result = image.crop((xStart, 0, xStart + squareSize, squareSize))
    result.load()
    return result

def splitStrip(image):
    """gets a list of squares from a horizontal strip of images"""
    squareSize = image.size[1]
    result = []
    for xStart in range(0, image.size[0], squareSize):
        subImage = image.crop((xStart, 0, xStart + squareSize, squareSize))
        subImage.load()
        result.append(subImage)
    return result
