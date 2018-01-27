import pyradox
import pyradox.format
import pyradox.token
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

csv.register_dialect('paradox', ParadoxDialect)
    
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
    headings = next(reader, None)
    
    if headings is None:
        raise ParseError('%s, row 1 (headings): csv file must have at least one row.' % filename)
    
    result = pyradox.Tree()
    
    for row_index, row_tokens in enumerate(reader):
        if len(row_tokens) == 0: continue # skip blank lines
        
        if len(row_tokens) != len(headings):
            warnings.warn_explicit('Row length (%d) should be same as headings length (%d).' % (len(row_tokens), len(headings)), ParseWarning, filename, row_index + 2)
        
        # first column is the key
        key = row_tokens[0]
        tree_row = pyradox.Tree()
        result[key] = tree_row
        
        for col_index in range(min(len(headings), len(row_tokens))):
            heading = headings[col_index]
            row_token = row_tokens[col_index]
            value = pyradox.token.make_primitive(row_token, default_token_type = 'str')
            tree_row.append(heading, row_token)
            
    return result 

def write_tree(tree, filename, column_specs, dialect, filter_function = None, sort_function = lambda key, value: key):
    """
    Writes a csv file from the given tree.
    column_specs: A list of (header, format_spec), one tuple per column. format_spec is as per pyradox.format.format_key_value.
    dialect: What dialect to use. Generally 'excel' or 'paradox'.
    filter_function: filter_function(key, value) determines whether to include each item.
    sort_function: sort_function(key, value) determines whether to include each item.
    """
    
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
