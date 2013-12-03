import csv
import os
import pyradox.config
import pyradox.txt
from PIL import Image, ImageFilter, ImageChops, ImageFont, ImageDraw

def neImage(image1, image2):
    """Returns a boolean image that is True where image1 != image2."""
    resultImage = Image.new('1', image1.size)
    diffImage = ImageChops.difference(image1, image2).point(lambda x: x != 0 and 255)
    bands = diffImage.split()
    for band in bands:
        resultImage = ImageChops.add(resultImage, band)
    return resultImage
    

def generateEdgeImage(image, edgeWidth=1):
    """Generates an edge mask from the image."""
    if edgeWidth < 3:
        resultImage = Image.new('L', image.size)
        """
        for xOffset, yOffset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            offsetImage = ImageChops.offset(image, xOffset, yOffset)
            currEdge = Image.new('L', image.size)
            currEdge.paste(127, None, neImage(offsetImage, image))
            resultImage = ImageChops.add(resultImage, currEdge)
        """
        for xOffset, yOffset in [(1, 0), (0, 1)]:
            offsetImage = ImageChops.offset(image, xOffset, yOffset)
            currEdge = Image.new('L', image.size)
            currEdge.paste(255, None, neImage(offsetImage, image))
            resultImage = ImageChops.add(resultImage, currEdge)
        return resultImage
    else:
        maxImage = image.filter(ImageFilter.MaxFilter(edgeWidth))
        minImage = image.filter(ImageFilter.MinFilter(edgeWidth))
        return neImage(maxImage, minImage)
    

class ProvinceMap():
    def __init__(self, basedir = pyradox.config.defaultBasedir):
        """Creates a province map using the base game directory specified, defaulting to the one in pyradox.config."""
        provincesBMP = os.path.join(basedir, 'map', 'provinces.bmp')
        definitionCSV = os.path.join(basedir, 'map', 'definition.csv')
        defaultMAP = os.path.join(basedir, 'map', 'default.map')
        

        self.provinceImage = Image.open(provincesBMP)

        csvReader = csv.reader(open(definitionCSV), delimiter = ';')
        self.provinceColorFromID = {}
        self.provinceIDFromColor = {}
        self.waterProvinces = set()
        self._adjacency = {} # lazy evaluation

        waterKeys = ('sea_starts', 'lakes')
        defaultTree = pyradox.txt.parseFile(defaultMAP, verbose=False)
        maxProvince = defaultTree['max_provinces']
        
        for key in waterKeys:
            if key in defaultTree:
                value = defaultTree[key]
                if isinstance(value, int):
                    for provinceID in range(value, maxProvince + 1):
                        self.waterProvinces.add(provinceID)
                else:
                    for provinceID in value:
                        self.waterProvinces.add(provinceID)
        
        for row in csvReader:
            try:
                provinceID = int(row[0])
                provinceColor = (int(row[1]), int(row[2]), int(row[3]))
                self.provinceColorFromID[provinceID] = provinceColor
                self.provinceIDFromColor[provinceColor] = provinceID
            except ValueError:
                pass

        # read province positions
        positionsTXT = os.path.join(basedir, 'map', 'positions.txt')
        positionsTree = pyradox.txt.parseFile(positionsTXT, verbose=False)
        self.positions = {}
        maxY = self.provinceImage.size[1] # use image coords
        for provinceID, data in positionsTree.items():
            positionData = data['position']
            self.positions[provinceID] = (positionData[2], maxY - positionData[3]) # second pair is unit position

    def isWaterProvince(self, provinceID):
        """ Return true iff province is a water province """
        return provinceID in self.waterProvinces

    def getAdjacent(self, provinceID):
        """ Returns a list of adjacent provinceIDs. """
        # get province bounding box
        provinceColorImage = ImageChops.constant(self.provinceImage, self.provinceColorFromID[provinceID])
        mask = ImageChops.invert(neImage(self.provinceImage, provinceColorImage))
        xMin, yMin, xMax, yMax = Image.getbbox(mask)
        
        # grow box
        #TODO: wraparound
        xMin = max(0, xMin - 1)
        yMin = max(0, yMin - 1)
        xMax = min(self.provinceImage.size[0]-1, xMax + 1)
        yMax = min(self.provinceImage.size[1]-1, yMax + 1)
        box = (xMin, yMin, xMax, yMax)

        # crop to area
        mask = mask.crop(box)
        growFilter = ImageFilter.Kernel((3, 3), (0, 1, 0, 1, 0, 1, 0, 1, 0))
        mask = mask.filter(growFilter)
        
        provinceColorImage = provinceColorImage.crop(box)
        blackImage = ImageChops.constant(provinceColorImage, (0, 0, 0))
        provinceColorImage = Image.composite(blackImage, provinceColorImage, mask)
        borderColors = provinceColorImage.getcolors()
        result = [color for (count, color) in borderColors]
        
    
    def generateImage(self, colormap,
                      scale = 1.0,
                      defaultLandColor = (51, 51, 51),
                      defaultWaterColor = (68, 107, 163),
                      edgeColor = (0, 0, 0),
                      edgeWidth = 1):
        """
        Given a colormap dict mapping provinceID -> color, colors the map and returns an PIL image.
        provinceIDs with no color get a default color depending on whether they are land or water.
        """

        # precompute map
        mergedMap = {}
        for provinceID, provinceColor in self.provinceColorFromID.items():
            if provinceID in colormap.keys():
                mergedMap[provinceColor] = colormap[provinceID]
            else:
                if provinceID in self.waterProvinces:
                    mergedMap[provinceColor] = defaultWaterColor
                else:
                    mergedMap[provinceColor] = defaultLandColor
        
        size = tuple(int(n * scale) for n in self.provinceImage.size)
        provinceImage = self.provinceImage.resize(size, Image.NEAREST)
        provinceImageData = provinceImage.getdata()
        result = Image.new(self.provinceImage.mode, size)
        result.putdata([mergedMap[pixel] for pixel in provinceImageData])

        if edgeWidth > 0:
            self.overlayEdges(result, edgeColor, edgeWidth)
        return result

    def overlayEdges(self, image, edgeColor = (0, 0, 0), edgeWidth = 1):
        """
        Overlays province edges on the target image.
        """
        provinceImage = self.provinceImage.resize(image.size, Image.NEAREST)
        edgeImage = generateEdgeImage(provinceImage, edgeWidth)
        image.paste(edgeColor, None, edgeImage)

    def overlayIcons(self, image, iconmap):
        """
        Given a dict mapping provinceID -> icon, overlays an icon on each province
        """
        relScaleX = image.size[0] / self.provinceImage.size[0]
        relScaleY = image.size[1] / self.provinceImage.size[1]

        for provinceID, icon in iconmap.items():
            posX, posY = self.positions[provinceID]
            scaledPosX, scaledPosY = posX * relScaleX, posY * relScaleY

            iconSizeX, iconSizeY = icon.size

            iconStartX = int(scaledPosX - iconSizeX / 2)
            iconStartY = int(scaledPosY - iconSizeY / 2)
            box = (iconStartX, iconStartY, iconStartX + iconSizeX, iconStartY + iconSizeY)
            image.paste(icon, box, icon)

    def overlayText(self, image, textmap, colormap = {}, fontsize = 12, fontfile='arial.ttf', defaultFontColor=(0, 0, 0)):
        """
        Given a textmap mapping provinceID -> text or (provinceID, ...) -> text, overlays text on each province
        Optional colormap definiting text color
        """
        relScaleX = image.size[0] / self.provinceImage.size[0]
        relScaleY = image.size[1] / self.provinceImage.size[1]

        font = ImageFont.truetype(fontfile, fontsize)
        draw = ImageDraw.Draw(image)

        for provinceID, text in textmap.items():
            if isinstance(provinceID, int):
                # single province: center on that province
                posX, posY = self.positions[provinceID]
            else:
                # set of provinces: find centroid
                centerX, centerY = 0.0, 0.0
                for subProvinceID in provinceID:
                    subPosX, subPosY = self.positions[subProvinceID]
                    centerX += subPosX
                    centerY += subPosY
                centerX /= len(provinceID)
                centerY /= len(provinceID)
                # then choose province nearest to centroid
                centerProvinceID = provinceID[0]
                posX, posY = self.positions[centerProvinceID]
                distSq = (posX - centerX) ** 2 + (posY - centerY) ** 2
                for subProvinceID in provinceID:
                    subPosX, subPosY = self.positions[subProvinceID]
                    subDistSq = (subPosX - centerX) ** 2 + (subPosY - centerY) ** 2
                    if subDistSq < distSq:
                        centerProvinceID = subProvinceID
                        posX, posY = subPosX, subPosY
                        distSq = subDistSq
                    
            scaledPosX, scaledPosY = posX * relScaleX, posY * relScaleY

            textSizeX, textSizeY = draw.textsize(text, font=font)

            textStartX = int(scaledPosX - textSizeX / 2)
            textStartY = int(scaledPosY - textSizeY / 2)

            if provinceID in colormap.keys():
                color = colormap[provinceID]
            else:
                color = defaultFontColor
            
            draw.text((textStartX, textStartY), text, font=font, fill=color)
                    

    

# unit test
if __name__ == "__main__":
    provinceMap = ProvinceMap(r'D:\Steam\steamapps\common\Europa Universalis IV')
    out = provinceMap.generateImage({1:(255, 255, 255)}, 0.25)
    out.save('test.png')
        
