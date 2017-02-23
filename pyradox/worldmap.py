import csv
import os
import collections
import warnings
import pyradox.config
import pyradox.txt
from PIL import Image, ImageFilter, ImageChops, ImageFont, ImageDraw

class MapWarning(Warning):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

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
    def __init__(self, game = None, flipY = False):
        """Creates a province map using the base game directory specified, defaulting to the one in pyradox.config."""
        basedir = pyradox.config.getBasedir(game)
        
        provincesBMP = os.path.join(basedir, 'map', 'provinces.bmp')
        definitionCSV = os.path.join(basedir, 'map', 'definition.csv')
        defaultMAP = os.path.join(basedir, 'map', 'default.map')
        
        self.provinceImage = Image.open(provincesBMP)

        if flipY:
            self.provinceImage = self.provinceImage.transpose(Image.FLIP_TOP_BOTTOM)

        with open(definitionCSV) as definitionFile:
            csvReader = csv.reader(definitionFile, delimiter = ';')
            self.provinceColorByID = {}
            self.provinceIDByColor = {}
            self.waterProvinces = set()
            self._adjacency = {} # lazy evaluation

            waterKeys = ('sea_starts', 'lakes')
            defaultTree = pyradox.txt.parseFile(defaultMAP, verbose=False)
            maxProvince = defaultTree['max_provinces']
            
            for key in waterKeys:
                for provinceID in defaultTree.findAll(key):
                    self.waterProvinces.add(provinceID)
            
            provinceCount = 0
            for row in csvReader:
                try:
                    provinceID = int(row[0])
                    provinceColor = (int(row[1]), int(row[2]), int(row[3]))
                    if row[4] in ("sea", "lake"): self.waterProvinces.add(provinceID) # HoI4
                    self.provinceColorByID[provinceID] = provinceColor
                    self.provinceIDByColor[provinceColor] = provinceID
                    provinceCount += 1
                except ValueError:
                    warnings.warn('Could not parse province definition from row "%s" of %s.' % (str(row), definitionCSV))
                    pass
            
            print("Read %d provinces from %s." % (provinceCount, definitionCSV))

        # read province positions
        self.positions = {}
        maxY = self.provinceImage.size[1] # use image coords
        positionsTXT = os.path.join(basedir, 'map', 'positions.txt')
        positionsTree = pyradox.txt.parseFile(positionsTXT, verbose=False)
        if len(positionsTree) > 0:
            
            for provinceID, data in positionsTree.items():
                if "position" in data:
                    positionData = [x for x in data.findAll('position')]
                    # second pair is unit position
                    self.positions[provinceID] = (positionData[2], maxY - positionData[3]) 
                    
                elif "text_position" in data:
                    positionData = data['text_position']
                    self.positions[provinceID] = (positionData['x'], maxY - positionData['y'])
                elif "building_position" in data:
                    _, positionData = data['building_position'].at(0)
                    self.positions[provinceID] = (positionData['x'], maxY - positionData['y'])
        else:
            # HoI4 fallback to unitstacks
            with open(os.path.join(basedir, 'map', 'unitstacks.txt')) as positionFile:
                csvReader = csv.reader(positionFile, delimiter = ';')
                for row in csvReader:
                    try:
                        provinceID = int(row[0])
                        provinceX = round(float(row[2]))
                        provinceY = round(float(row[4]))
                        self.positions[provinceID] = (provinceX, maxY - provinceY)
                    except ValueError:
                        pass
                
    def isWaterProvince(self, provinceID):
        """ Return true iff province is a water province """
        return provinceID in self.waterProvinces

    def getAdjacent(self, provinceID):
        """ Returns a list of adjacent provinceIDs. """
        # get province bounding box
        provinceColorImage = ImageChops.constant(self.provinceImage, self.provinceColorByID[provinceID])
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
                      defaultLandColor = (51, 51, 51),
                      defaultWaterColor = (68, 107, 163),
                      edgeColor = (0, 0, 0),
                      edgeWidth = 1,
                      edgeGroups = None):
        """
        Given a colormap dict mapping provinceID -> color, colors the map and returns an PIL image.
        provinceIDs with no color get a default color depending on whether they are land or water.
        """

        # precompute map provinceColor -> result color
        mergedMap = collections.defaultdict(lambda: defaultWaterColor)
        for provinceID, provinceColor in self.provinceColorByID.items():
            if provinceID in colormap.keys():
                mergedMap[provinceColor] = colormap[provinceID]
            else:
                if provinceID in self.waterProvinces:
                    mergedMap[provinceColor] = defaultWaterColor
                else:
                    mergedMap[provinceColor] = defaultLandColor
        
        result = Image.new(self.provinceImage.mode, self.provinceImage.size)
        result.putdata([mergedMap[pixel] for pixel in self.provinceImage.getdata()])

        if edgeWidth > 0:
            self.overlayEdges(result, edgeColor, edgeWidth, groups = edgeGroups)
        return result

    def overlayEdges(self, image, edgeColor = (0, 0, 0), edgeWidth = 1, groups = None):
        """
        Overlays province edges on the target image.
        Provinces may be grouped together using the groups argument
        [[provinceIDinGroup0, provinceIDinGroup0, ...], [provinceIDinGroup1, provinceIDinGroup1, ...], ...]
        """
        
        if groups is not None:
            # map provinceColor -> result color
            colorMap = {}
            
            for group in groups:
                # color all provinces in the group according to the first province in the group
                groupColor = self.provinceColorByID[group[0]]
                for provinceID in group:
                    originalColor = self.provinceColorByID[provinceID]
                    colorMap[originalColor] = groupColor
            
            # perform the coloring
            provinceImage = Image.new(self.provinceImage.mode, image.size)
            def mapColor(pixel):
                if pixel in colorMap: return colorMap[pixel]
                else:
                    # map all ungrouped provinces to the same group
                    if 'default' not in colorMap:
                        colorMap['default'] = pixel
                    return colorMap['default']
            
            provinceImage.putdata([mapColor(pixel) for pixel in self.provinceImage.getdata()])
        else:
            provinceImage = self.provinceImage.resize(image.size, Image.NEAREST)
                    
        edgeImage = generateEdgeImage(provinceImage, edgeWidth)
        image.paste(edgeColor, None, edgeImage)

    def overlayIcons(self, image, iconmap, offsetmap = {}, defaultOffset = (0, 0)):
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
            
            if provinceID in offsetmap.keys():
                iconStartX += offsetmap[provinceID][0]
                iconStartY += offsetmap[provinceID][1]
            else:
                iconStartX += defaultOffset[0]
                iconStartY += defaultOffset[1]
            
            box = (iconStartX, iconStartY, iconStartX + iconSizeX, iconStartY + iconSizeY)
            image.paste(icon, box, icon)

    def overlayText(self, image, textmap, colormap = {}, offsetmap = {}, fontsize = 9, fontfile='tahoma.ttf', defaultFontColor=(0, 0, 0), antialias = False, defaultOffset = (0, 0)):
        """
        Given a textmap mapping provinceID -> text or (provinceID, ...) -> text, overlays text on each province
        Optional colormap definiting text color.
        offset: pixels to offset text.
        """
        relScaleX = image.size[0] / self.provinceImage.size[0]
        relScaleY = image.size[1] / self.provinceImage.size[1]

        font = ImageFont.truetype(fontfile, fontsize)
        draw = ImageDraw.Draw(image)

        if not antialias: draw.fontmode = "1"

        for provinceID, text in textmap.items():
            if isinstance(provinceID, int):
                # single province: center on that province
                if provinceID not in self.positions:
                    warnings.warn(MapWarning('Textmap references province ID %d with no position for text string "%s".' % (provinceID, text)))
                    continue
                posX, posY = self.positions[provinceID]
            else:
                # set of provinces: find centroid
                centerX, centerY = 0.0, 0.0
                provinceCount = 0
                for subProvinceID in provinceID:
                    if subProvinceID not in self.positions:
                        warnings.warn(MapWarning('Textmap references province ID %d with no position for text string "%s".' % (subProvinceID, text)))
                        continue
                    centerProvinceID = subProvinceID
                    subPosX, subPosY = self.positions[subProvinceID]
                    centerX += subPosX
                    centerY += subPosY
                    provinceCount += 1
                    
                if provinceCount == 0:
                    warnings.warn(MapWarning('No valid provinces were found for text string "%s".' % (subProvinceID, text)))
                    continue
                
                centerX /= provinceCount
                centerY /= provinceCount
                
                # then choose province nearest to centroid
                posX, posY = self.positions[centerProvinceID]
                distSq = (posX - centerX) ** 2 + (posY - centerY) ** 2
                for subProvinceID in provinceID:
                    if subProvinceID not in self.positions:
                        continue # already warned
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
            
            if provinceID in offsetmap.keys():
                textStartX += offsetmap[provinceID][0]
                textStartY += offsetmap[provinceID][1]
            else:
                textStartX += defaultOffset[0]
                textStartY += defaultOffset[1]

            if provinceID in colormap.keys():
                color = colormap[provinceID]
            else:
                color = defaultFontColor
            
            draw.text((textStartX, textStartY), text, font=font, fill=color)
