import csv
import os
import warnings
import pyradox.primitive

class ParseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
        
class ParseWarning(Warning):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class ParadoxDialect(csv.Dialect):
    delimiter = ';'
    lineterminator = '\n'
    quoting = csv.QUOTE_NONE # no quotes AFAICT
    strict = True

def parseFile(filename, verbose=False):
    f = open(filename)
    lines = f.readlines()
    f.close()
    if verbose: print('Parsing file %s.' % filename)
    return parse(lines, filename)
    
def parseDir(dirname, verbose=False):
    """Given a directory, iterate over the content of the .csv files in that directory"""
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        if os.path.isfile(fullpath):
            _, ext = os.path.splitext(fullpath)
            if ext == ".csv":
                yield filename, parseFile(fullpath, verbose)

def parse(lines, filename):
    reader = csv.reader(lines, dialect = ParadoxDialect)
    headerTokens = next(reader, None)
    if headerTokens is None:
        raise ParseError('%s, row 1 (headers): csv file must have at least one row' % filename)
    headers = [x.lower() for x in headerTokens]
    result = Table(headers)
    for i, rowTokens in enumerate(reader):
        if len(rowTokens) == 0: continue
        if len(rowTokens) != len(headers):
            warnings.warn(ParseWarning('%s, row %d: row length (%d) should be same as headers length (%d)' % (filename, i + 2, len(rowTokens), len(headers))))
            for i in range(len(rowTokens), len(headers)):
                rowTokens.append('')
            rowTokens = rowTokens[:len(headers)]
        result.addRow([pyradox.primitive.makePrimitive(token, defaultTokenType = 'str') for token in rowTokens])
    return result
    
class Table():
    def __init__(self, headers):
        self._headers = headers
        self._data = []

    def addRow(self, row):
        self._data.append(row)
        
    def __iter__(self):
        for row in self._data:
            yield row
            
    def getHeaders(self):
        return self._headers
            
    def getHeaderIndex(self, header):
        return self._headers.index(header.lower())
            
    def selectColumns(self, headers):
        headerIndexes = []
        for header in headers:
            if isinstance(header, int):
                headerIndexes.append(header)
            else:
                headerIndexes.append(self.getHeaderIndex(header))
                
        for row in self._data:
            yield [row[index] for index in headerIndexes]
    