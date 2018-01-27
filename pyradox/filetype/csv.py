import pyradox
import pyradox.format
from pyradox.error import *

import csv
import os
import warnings

encoding = 'cp1252'

class ParadoxDialect(csv.Dialect):
    delimiter = ';'
    lineterminator = '\n'
    quoting = csv.QUOTE_NONE # no quotes AFAICT
    strict = True

def parse_file(filename, verbose=False):
    with open(filename, encoding=encoding) as f:
        lines = f.readlines()
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
    result = pyradox.Table(headings)
    for i, row_tokens in enumerate(reader):
        row_tokens = row_tokens[:-1]
        if len(row_tokens) == 0: continue
        if len(row_tokens) != len(headings):
            warnings.warn(ParseWarning('%s, row %d: row length (%d) should be same as headings length (%d)' % (filename, i + 2, len(row_tokens), len(headings))))
            for i in range(len(row_tokens), len(headings)):
                row_tokens.append('')
            row_tokens = row_tokens[:len(headings)]
        result.add_row([pyradox.token.make_primitive(token, default_token_type = 'str') for token in row_tokens])
    return result 

def write_csv(filename, tree, column_specs, dialect, filter_function = None, sort_function = lambda key, value: key):
    """
    Writes a csv file from the given tree.
    column_specs: A list of (header, format_spec), one tuple per column. format_spec is as per pyradox.format.format_key_value.
    dialect: What dialect to use. Generally 'excel' or 'paradox'.
    filter_function: filter_function(item) determines whether to include each item.
    sort_function: sort_function(item) determines whether to include each item.
    """
    
    if dialect == 'paradox':
        dialect = ParadoxDialect
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, dialect = dialect)
        
        # workaround for excel interpreting leading ID as special file type
        if dialect == 'excel' and column_specs[0][0][:2] == 'ID':
            header_row = [column_specs[0][0].lower()] + [header for header, format_spec in column_specs[1:]]
        else:
            header_row = [header for header, format_spec in column_specs]
        
        writer.writerow(header_row)
        
        for key, value in sorted(tree.items(), key = lambda item: sort_function(*item)):
            if filter_function is not None and not filter_function(key, value): continue
            
            writer.writerow([pyradox.format.format_key_value(key, value, format_spec) for header, format_spec in column_specs])
