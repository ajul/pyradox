import pyradox.format
import re

class Dialect:
    @staticmethod
    def table_begin(**kwargs):
        return ''
        
    table_end = ''
    row_delimiter = '' # placed between each row, but not before the first or after the last
    
    header_begin = ''
    header_end = '\n'
    header_cell_begin = ''
    header_cell_end = ''
    header_cell_delimiter = '' # placed between cells, but not before the first or after the last
    
    row_begin = ''
    row_end = '\n'
    
    @staticmethod
    def row_cell_begin(s):
        return ''
    
    row_cell_end = ''
    row_cell_delimiter = '' # placed between cells, but not before the first or after the last

class WikiDialect(Dialect):
    @staticmethod
    def table_begin(table_classes = ["wikitable sortable"]):
        return '{| class = "%s" style="text-align: right;"\n' % ' '.join(table_classes)
    
    table_end = '|}\n'
    row_delimiter = '|-\n'
    
    header_begin = '! '
    header_cell_delimiter = ' !! '
    
    row_begin = '| '
    
    @staticmethod
    def row_cell_begin(s):
        if guess_is_numeric(s):
            return ''
        else:
            return 'style="text-align: left;" | '
        
    row_cell_delimiter = ' || '

class HtmlDialect(Dialect):
    @staticmethod
    def table_begin(table_classes):
        return '<table class = "%s">\n' % ' '.join(table_classes)
        
    table_end = '</table>\n'
    
    header_begin = '    <tr>'
    header_end = '</tr>\n'
    header_cell_begin = '<th>'
    header_cell_end = '</th>'
    
    row_begin = '    <tr>'
    row_end = '</tr>\n'
    @staticmethod
    def row_cell_begin(s):
        return '<td>'
    row_cell_end = '</td>'

dialects = {
    'wiki' : WikiDialect,
    'html' : HtmlDialect,
}

def guess_is_numeric(s):
    # remove wiki templates
    match = re.match(r'\{\{.*?\|(.*?)\}\}', s)
    if match is not None:
        s = match.group(1)
        
    # remove whitepsace, percent
    s = s.lstrip()
    s = s.rstrip()
    s = s.rstrip('%')
    
    if len(s) == 0:
        return True
        
    try:
        float(s)
    except ValueError:
        return False
    return True

def default_column_specs(key, row):
    column_specs = [('id', None)]
    for k, v in row.items():
        column_specs.append((k, '%%(%s)s' % k))
    return column_specs

def filter_and_sort_tree(tree, filter_function = None, sort_function = None):
    if filter_function is None: filter_function = lambda key, row: True
    if sort_function is None: sort_function = lambda key, row: 0
    
    for key, row in sorted(tree.items(), key = lambda item: sort_function(*item)):
        if filter_function(key, row): yield key, row

def make_table(tree, dialect, column_specs = None, filter_function = None, sort_function = None, **kwargs):
    if isinstance(dialect, str):
        dialect = dialects[dialect]
    
    table = dialect.table_begin(**kwargs)
    
    rows = list(filter_and_sort_tree(tree, filter_function, sort_function))
    
    if column_specs is None:
        column_specs = default_column_specs(*rows[0])
        
    table_rows = []
    
    table_row = [dialect.header_cell_begin + header + dialect.header_cell_end for header, _ in column_specs]
    table_row = dialect.header_begin + dialect.header_cell_delimiter.join(table_row) + dialect.header_end
    table_rows.append(table_row)
        
    for key, row in rows:
        table_row = []
        for _, format_spec in column_specs:
            cell_contents = apply_format_spec(key, row, format_spec)
            cell_contents = dialect.row_cell_begin(cell_contents) + cell_contents + dialect.row_cell_end
            table_row.append(cell_contents)
        table_row = dialect.row_begin + dialect.row_cell_delimiter.join(table_row) + dialect.row_end
        table_rows.append(table_row)
    
    table += dialect.row_delimiter.join(table_rows)
    table += dialect.table_end
    
    return table

def make_tables(tree, dialect, split_function, filter_function = None, *args, **kwargs):
    # TODO: better version
    
    split_set = set()
    
    if filter_function is None: filter_function = lambda key, row: True
    
    for key, row in tree.items():
        if filter_function(key, row):
            split_id = split_function(key, row)
            split_set.add(split_id)
        
    result = ''
    
    for split_id in sorted(split_set):
        filter_function = lambda k, v: split_function(k, v) == split_id
        result += make_table(tree, dialect, filter_function = filter_function, *args, **kwargs)
        result += '\n'
    
    return result
    
def apply_format_spec(key, row, format_spec):
    """
    Produces a string from a key-row pair based on the format_spec.
    row is typically a Tree.
    format_spec can be:
        A function f(key, row). In this case the return row is the return row of f.
        A string s. In this case the return row is s % format_spec.
        None. In this case the return row is human_string(key, True).
    """
    if callable(format_spec):
        try:
            return format_spec(key, row)
        except ZeroDivisionError:
            return ''
    elif format_spec is None:
        return pyradox.format.human_string(key, True)
    else:
        try:
            return format_spec % row
        except TypeError:
            return ''

def wiki_colored_percent_string(x, number_format = '%+d%%', color = True):
    # color can be a fixed color, True (+green), or False (-green)
    if x == 0 or x is None: return ""
    if color in (True, False):
        if (x > 0.0) == color:
            return ("{{green|%s}}" % number_format) % (x * 100.0)
        else:
            return ("{{red|%s}}" % number_format) % (x * 100.0)
    else:
        return ("{{%%s|%s}}" % number_format) % (color, x * 100.0)