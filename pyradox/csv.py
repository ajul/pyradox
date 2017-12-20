import csv
import os
import warnings
import pyradox.primitive
import pyradox.struct
import pyradox.table

from pyradox.error import ParseError, ParseWarning

encoding = 'cp1252'

class ParadoxDialect(csv.Dialect):
    delimiter = ';'
    lineterminator = '\n'
    quoting = csv.QUOTE_NONE # no quotes AFAICT
    strict = True

def parse_file(filename, verbose=False):
    f = open(filename, encoding=encoding)
    lines = f.readlines()
    f.close()
    if verbose: print('Parsing file %s.' % filename)
    return parse(lines, filename)
    
def parse_dir(dirname, verbose=False):
    """Given a directory, iterate over the content of the .csv files in that directory"""
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        if os.path.isfile(fullpath):
            _, ext = os.path.splitext(fullpath)
            if ext == ".csv":
                yield filename, parse_file(fullpath, verbose)

def parse(lines, filename):
    reader = csv.reader(lines, dialect = ParadoxDialect)
    heading_tokens = next(reader, None)
    if heading_tokens is None:
        raise ParseError('%s, row 1 (headings): csv file must have at least one row' % filename)
    headings = [x.lower() for x in heading_tokens[:-1]]
    result = pyradox.table.Table(headings)
    for i, row_tokens in enumerate(reader):
        row_tokens = row_tokens[:-1]
        if len(row_tokens) == 0: continue
        if len(row_tokens) != len(headings):
            warnings.warn(ParseWarning('%s, row %d: row length (%d) should be same as headings length (%d)' % (filename, i + 2, len(row_tokens), len(headings))))
            for i in range(len(row_tokens), len(headings)):
                row_tokens.append('')
            row_tokens = row_tokens[:len(headings)]
        result.add_row([pyradox.primitive.make_primitive(token, default_token_type = 'str') for token in row_tokens])
    return result 
    
