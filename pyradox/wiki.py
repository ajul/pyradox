import pyradox.format

def makeWikitable(tree, columnSpecs, filterFunction = None):
    # columnSpecs: [(header, content) ...]
    # each key, value pair produces a row
    # content can be one of the following:
    # * a function f -> f(key, value)
    # * None -> pyradox.format.humanString(key, True)
    # * a format string s -> s % value

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
                try:
                    result += columnSpec(key, value)
                except ZeroDivisionError:
                    pass
            elif columnSpec is None:
                result += pyradox.format.humanString(key, True)
            else:
                try:
                    result += columnSpec % value
                except TypeError:
                    pass
            result += '\n'
    result += '|}\n'
    return result
