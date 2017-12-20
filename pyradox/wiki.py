import re
import pyradox.format

def make_wikitable(tree, column_specs, filter_function = None, sort_function = lambda item: item[0], table_style = "text-align: right;", collapse = False, sortable = True):
    # column_specs: [(header, content, maybe_cell_style) ...]
    # each key, value pair produces a row
    # content can be one of the following:
    # * a function f -> f(key, value)
    # * None -> pyradox.format.human_string(key, True)
    # * a format string s -> s % value
    
    # By default aligns all numbers right and everything else left.
    
    result = '{|class = "wikitable'
    if sortable:
        result += ' sortable'
    if collapse:
        result += ' mw-collapsible mw-collapsed'
    result += '"'
    
    # table format
    if table_style:
        result += ' style="%s"' % table_style
    
    result += '\n'  
    
    # header
    for column_spec in column_specs:
        header = column_spec[0]
        result += '! %s \n' % header

    # body
    for key, value in sorted(tree.items(), key = sort_function):
        if filter_function is not None and not filter_function(key, value): continue
        result += '|-\n'
        for column_spec in column_specs:
            result += '| '
            
                
            contents = column_spec[1]
            
            if callable(contents):
                try:
                    content_string = contents(key, value)
                except ZeroDivisionError:
                    content_string = ''
            elif contents is None:
                content_string = pyradox.format.human_string(key, True)
            else:
                try:
                    content_string = contents % value
                except TypeError:
                    content_string = ''
                    
            if len(column_spec) >= 3:
                cell_style = column_spec[2]
                if cell_style is not None:
                    result += 'style="%s" | ' % cell_style
            elif content_string != '':
                if not re.search(r'(\+|-)?\d+(\.\d*)?%?', content_string):
                    result += 'style="text-align: left;" | ' 
            result += content_string
            
            result += '\n'
    result += '|}\n'
    return result

def colored_percent_string(x, number_format = '%+d%%', color = True):
    # color can be a fixed color, True (+green), or False (-green)
    if x == 0 or x is None: return ""
    if color in (True, False):
        if (x > 0.0) == color:
            return ("{{green|%s}}" % number_format) % (x * 100.0)
        else:
            return ("{{red|%s}}" % number_format) % (x * 100.0)
    else:
        return ("{{%%s|%s}}" % number_format) % (color, x * 100.0)
