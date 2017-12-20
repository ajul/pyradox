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

def ne_image(image1, image2):
    """Returns a boolean image that is True where image1 != image2."""
    result_image = Image.new('1', image1.size)
    diff_image = ImageChops.difference(image1, image2).point(lambda x: x != 0 and 255)
    bands = diff_image.split()
    for band in bands:
        result_image = ImageChops.add(result_image, band)
    return result_image
    

def generate_edge_image(image, edge_width=1):
    """Generates an edge mask from the image."""
    if edge_width < 3:
        result_image = Image.new('L', image.size)
        """
        for x_offset, y_offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            offset_image = ImageChops.offset(image, x_offset, y_offset)
            curr_edge = Image.new('L', image.size)
            curr_edge.paste(127, None, ne_image(offset_image, image))
            result_image = ImageChops.add(result_image, curr_edge)
        """
        for x_offset, y_offset in [(1, 0), (0, 1)]:
            offset_image = ImageChops.offset(image, x_offset, y_offset)
            curr_edge = Image.new('L', image.size)
            curr_edge.paste(255, None, ne_image(offset_image, image))
            result_image = ImageChops.add(result_image, curr_edge)
        return result_image
    else:
        max_image = image.filter(ImageFilter.MaxFilter(edge_width))
        min_image = image.filter(ImageFilter.MinFilter(edge_width))
        return ne_image(max_image, min_image)
    

class ProvinceMap():
    def __init__(self, game = None, flip_y = False):
        """Creates a province map using the base game directory specified, defaulting to the one in pyradox.config."""
        basedir = pyradox.config.get_basedir(game)
        
        provinces_bmp = os.path.join(basedir, 'map', 'provinces.bmp')
        definition_csv = os.path.join(basedir, 'map', 'definition.csv')
        default_map = os.path.join(basedir, 'map', 'default.map')
        
        self.province_image = Image.open(provinces_bmp)

        if flip_y:
            self.province_image = self.province_image.transpose(Image.FLIP_TOP_BOTTOM)

        with open(definition_csv) as definition_file:
            csv_reader = csv.reader(definition_file, delimiter = ';')
            self.province_color_by_id = {}
            self.province__idb_y_color = {}
            self.water_provinces = set()
            self._adjacency = {} # lazy evaluation

            water_keys = ('sea_starts', 'lakes')
            default_tree = pyradox.txt.parse_file(default_map, verbose=False)
            max_province = default_tree['max_provinces']
            
            for key in water_keys:
                for province_id in default_tree.find_all(key):
                    self.water_provinces.add(province_id)
            
            province_count = 0
            for row in csv_reader:
                try:
                    province_id = int(row[0])
                    province_color = (int(row[1]), int(row[2]), int(row[3]))
                    if row[4] in ("sea", "lake"): self.water_provinces.add(province_id) # HoI4
                    self.province_color_by_id[province_id] = province_color
                    self.province__idb_y_color[province_color] = province_id
                    province_count += 1
                except ValueError:
                    warnings.warn('Could not parse province definition from row "%s" of %s.' % (str(row), definition_csv))
                    pass
            
            print("Read %d provinces from %s." % (province_count, definition_csv))

        # read province positions
        self.positions = {}
        max_y = self.province_image.size[1] # use image coords
        positions_txt = os.path.join(basedir, 'map', 'positions.txt')
        positions_tree = pyradox.txt.parse_file(positions_txt, verbose=False)
        if len(positions_tree) > 0:
            
            for province_id, data in positions_tree.items():
                if "position" in data:
                    position_data = [x for x in data.find_all('position')]
                    # second pair is unit position
                    self.positions[province_id] = (position_data[2], max_y - position_data[3]) 
                    
                elif "text_position" in data:
                    position_data = data['text_position']
                    self.positions[province_id] = (position_data['x'], max_y - position_data['y'])
                elif "building_position" in data:
                    _, position_data = data['building_position'].at(0)
                    self.positions[province_id] = (position_data['x'], max_y - position_data['y'])
        else:
            # HoI4 fallback to unitstacks
            with open(os.path.join(basedir, 'map', 'unitstacks.txt')) as position_file:
                csv_reader = csv.reader(position_file, delimiter = ';')
                for row in csv_reader:
                    try:
                        province_id = int(row[0])
                        province_x = round(float(row[2]))
                        province_y = round(float(row[4]))
                        self.positions[province_id] = (province_x, max_y - province_y)
                    except ValueError:
                        pass
                
    def is_water_province(self, province_id):
        """ Return true iff province is a water province """
        return province_id in self.water_provinces

    def get_adjacent(self, province_id):
        """ Returns a list of adjacent province_id_s. """
        # get province bounding box
        province_color_image = ImageChops.constant(self.province_image, self.province_color_by_id[province_id])
        mask = ImageChops.invert(ne_image(self.province_image, province_color_image))
        x_min, y_min, x_max, y_max = Image.getbbox(mask)
        
        # grow box
        #TODO: wraparound
        x_min = max(0, x_min - 1)
        y_min = max(0, y_min - 1)
        x_max = min(self.province_image.size[0]-1, x_max + 1)
        y_max = min(self.province_image.size[1]-1, y_max + 1)
        box = (x_min, y_min, x_max, y_max)

        # crop to area
        mask = mask.crop(box)
        grow_filter = ImageFilter.Kernel((3, 3), (0, 1, 0, 1, 0, 1, 0, 1, 0))
        mask = mask.filter(grow_filter)
        
        province_color_image = province_color_image.crop(box)
        black_image = ImageChops.constant(province_color_image, (0, 0, 0))
        province_color_image = Image.composite(black_image, province_color_image, mask)
        border_colors = province_color_image.getcolors()
        result = [color for (count, color) in border_colors]
        
    
    def generate_image(self, colormap,
                      default_land_color = (51, 51, 51),
                      default_water_color = (68, 107, 163),
                      edge_color = (0, 0, 0),
                      edge_width = 1,
                      edge_groups = None):
        """
        Given a colormap dict mapping province_id -> color, colors the map and returns an PIL image.
        province_id_s with no color get a default color depending on whether they are land or water.
        """

        # precompute map province_color -> result color
        merged_map = collections.defaultdict(lambda: default_water_color)
        for province_id, province_color in self.province_color_by_id.items():
            if province_id in colormap.keys():
                merged_map[province_color] = colormap[province_id]
            else:
                if province_id in self.water_provinces:
                    merged_map[province_color] = default_water_color
                else:
                    merged_map[province_color] = default_land_color
        
        result = Image.new(self.province_image.mode, self.province_image.size)
        result.putdata([merged_map[pixel] for pixel in self.province_image.getdata()])

        if edge_width > 0:
            self.overlay_edges(result, edge_color, edge_width, groups = edge_groups)
        return result

    def overlay_edges(self, image, edge_color = (0, 0, 0), edge_width = 1, groups = None):
        """
        Overlays province edges on the target image.
        Provinces may be grouped together using the groups argument
        [[province_id_in_group0, province_id_in_group0, ...], [province_id_in_group1, province_id_in_group1, ...], ...]
        """
        
        if groups is not None:
            # map province_color -> result color
            color_map = {}
            
            for group in groups:
                # color all provinces in the group according to the first province in the group
                group_color = self.province_color_by_id[group[0]]
                for province_id in group:
                    original_color = self.province_color_by_id[province_id]
                    color_map[original_color] = group_color
            
            # perform the coloring
            province_image = Image.new(self.province_image.mode, image.size)
            def map_color(pixel):
                if pixel in color_map: return color_map[pixel]
                else:
                    # map all ungrouped provinces to the same group
                    if 'default' not in color_map:
                        color_map['default'] = pixel
                    return color_map['default']
            
            province_image.putdata([map_color(pixel) for pixel in self.province_image.getdata()])
        else:
            province_image = self.province_image.resize(image.size, Image.NEAREST)
                    
        edge_image = generate_edge_image(province_image, edge_width)
        image.paste(edge_color, None, edge_image)

    def overlay_icons(self, image, iconmap, offsetmap = {}, default_offset = (0, 0)):
        """
        Given a dict mapping province_id -> icon, overlays an icon on each province
        """
        rel_scale_x = image.size[0] / self.province_image.size[0]
        rel_scale_y = image.size[1] / self.province_image.size[1]

        for province_id, icon in iconmap.items():
            pos_x, pos_y = self.positions[province_id]
            scaled_pos_x, scaled_pos_y = pos_x * rel_scale_x, pos_y * rel_scale_y

            icon_size_x, icon_size_y = icon.size

            icon_start_x = int(scaled_pos_x - icon_size_x / 2)
            icon_start_y = int(scaled_pos_y - icon_size_y / 2)
            
            if province_id in offsetmap.keys():
                icon_start_x += offsetmap[province_id][0]
                icon_start_y += offsetmap[province_id][1]
            else:
                icon_start_x += default_offset[0]
                icon_start_y += default_offset[1]
            
            box = (icon_start_x, icon_start_y, icon_start_x + icon_size_x, icon_start_y + icon_size_y)
            image.paste(icon, box, icon)

    def overlay_text(self, image, textmap, colormap = {}, offsetmap = {}, fontsize = 9, fontfile='tahoma.ttf', default_font_color=(0, 0, 0), antialias = False, default_offset = (0, 0)):
        """
        Given a textmap mapping province_id -> text or (province_id, ...) -> text, overlays text on each province
        Optional colormap definiting text color.
        offset: pixels to offset text.
        """
        rel_scale_x = image.size[0] / self.province_image.size[0]
        rel_scale_y = image.size[1] / self.province_image.size[1]

        font = ImageFont.truetype(fontfile, fontsize)
        draw = ImageDraw.Draw(image)

        if not antialias: draw.fontmode = "1"

        for province_id, text in textmap.items():
            if isinstance(province_id, int):
                # single province: center on that province
                if province_id not in self.positions:
                    warnings.warn(MapWarning('Textmap references province ID %d with no position for text string "%s".' % (province_id, text)))
                    continue
                pos_x, pos_y = self.positions[province_id]
            else:
                # set of provinces: find centroid
                center_x, center_y = 0.0, 0.0
                province_count = 0
                for sub_province_id in province_id:
                    if sub_province_id not in self.positions:
                        warnings.warn(MapWarning('Textmap references province ID %d with no position for text string "%s".' % (sub_province_id, text)))
                        continue
                    center_province_id = sub_province_id
                    sub_pos_x, sub_pos_y = self.positions[sub_province_id]
                    center_x += sub_pos_x
                    center_y += sub_pos_y
                    province_count += 1
                    
                if province_count == 0:
                    warnings.warn(MapWarning('No valid provinces were found for text string "%s".' % (sub_province_id, text)))
                    continue
                
                center_x /= province_count
                center_y /= province_count
                
                # then choose province nearest to centroid
                pos_x, pos_y = self.positions[center_province_id]
                dist_sq = (pos_x - center_x) ** 2 + (pos_y - center_y) ** 2
                for sub_province_id in province_id:
                    if sub_province_id not in self.positions:
                        continue # already warned
                    sub_pos_x, sub_pos_y = self.positions[sub_province_id]
                    sub_dist_sq = (sub_pos_x - center_x) ** 2 + (sub_pos_y - center_y) ** 2
                    if sub_dist_sq < dist_sq:
                        center_province_id = sub_province_id
                        pos_x, pos_y = sub_pos_x, sub_pos_y
                        dist_sq = sub_dist_sq
                    
            scaled_pos_x, scaled_pos_y = pos_x * rel_scale_x, pos_y * rel_scale_y

            text_size_x, text_size_y = draw.textsize(text, font=font)

            text_start_x = int(scaled_pos_x - text_size_x / 2)
            text_start_y = int(scaled_pos_y - text_size_y / 2)
            
            if province_id in offsetmap.keys():
                text_start_x += offsetmap[province_id][0]
                text_start_y += offsetmap[province_id][1]
            else:
                text_start_x += default_offset[0]
                text_start_y += default_offset[1]

            if province_id in colormap.keys():
                color = colormap[province_id]
            else:
                color = default_font_color
            
            draw.text((text_start_x, text_start_y), text, font=font, fill=color)
