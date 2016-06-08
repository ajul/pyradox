import re
import pyradox.format

def makeWikitable(tree, columnSpecs, filterFunction = None, sortFunction = lambda item: item[0], tableStyle = "text-align: right;", collapse = False, sortable = True):
    # columnSpecs: [(header, content, maybeCellStyle) ...]
    # each key, value pair produces a row
    # content can be one of the following:
    # * a function f -> f(key, value)
    # * None -> pyradox.format.humanString(key, True)
    # * a format string s -> s % value
    
    # By default aligns all numbers right and everything else left.
    
    result = '{|class = "wikitable'
    if sortable:
        result += ' sortable'
    if collapse:
        result += ' mw-collapsible mw-collapsed'
    result += '"'
    
    # table format
    if tableStyle:
        result += ' style="%s"' % tableStyle
    
    result += '\n'  
    
    # header
    for columnSpec in columnSpecs:
        header = columnSpec[0]
        result += '! %s \n' % header

    # body
    for key, value in sorted(tree.items(), key = sortFunction):
        if filterFunction is not None and not filterFunction(key, value): continue
        result += '|-\n'
        for columnSpec in columnSpecs:
            result += '| '
            
                
            contents = columnSpec[1]
            
            if callable(contents):
                try:
                    contentString = contents(key, value)
                except ZeroDivisionError:
                    contentString = ''
            elif contents is None:
                contentString = pyradox.format.humanString(key, True)
            else:
                try:
                    contentString = contents % value
                except TypeError:
                    contentString = ''
                    
            if len(columnSpec) >= 3:
                cellStyle = columnSpec[2]
                if cellStyle is not None:
                    result += 'style="%s" | ' % cellStyle
            elif contentString != '':
                if not re.search(r'(\+|-)?\d+(\.\d*)?%?', contentString):
                    result += 'style="text-align: left;" | ' 
            result += contentString
            
            result += '\n'
    result += '|}\n'
    return result

def coloredPercentString(x, numberFormat = '%+d%%', color = True):
    # color can be a fixed color, True (+green), or False (-green)
    if x == 0 or x is None: return ""
    if color in (True, False):
        if (x > 0.0) == color:
            return ("{{green|%s}}" % numberFormat) % (x * 100.0)
        else:
            return ("{{red|%s}}" % numberFormat) % (x * 100.0)
    else:
        return ("{{%%s|%s}}" % numberFormat) % (color, x * 100.0)
