import pyradox.format

def makeWikiString(value):
    if isinstance(value, float):
        return "%0.3f" % value
    elif value is None:
        return ""
    else:
        return str(value)

def makeWikitable(tree, columnSpecs, filterFunction = None):
    # columnSpecs: [(header, content) ...]
    # each key, value pair produces a row
    # content can be one of the following:
    # * a function f -> f(key, value)
    # * None -> pyradox.format.humanString(key, True)
    # * a subkey sk -> value[sk]

    result = '{|class = "wikitable sortable"\n'
    # header
    for header, _ in columnSpecs:
        result += '! %s \n' % header

    # body
    for key, value in tree.items():
        if filterFunction is not None and not filterFunction(key, value): continue
        result += '|-\n'
        for _, columnSpec in columnSpecs:
            result += '| '
            if callable(columnSpec):
                result += columnSpec(key, value)
            elif columnSpec is None:
                result += pyradox.format.humanString(key, True)
            else:
                result += makeWikiString(value[columnSpec])
            result += '\n'
    result += '|}\n'
    return result
