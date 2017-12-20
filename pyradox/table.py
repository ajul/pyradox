import pyradox.struct

class Table():
    def __init__(self, headings):
        self._headings = headings
        self._data = []

    def make_row(self, row):
        if hasattr(row, 'items'):
            return {k: v for k, v in row.items()}
        else:
            return {k: v for k, v in zip(self._headings, row)}

    def add_row(self, row):
        self._data.append(self.make_row(row))
        
    def __iter__(self):
        for row in self._data:
            yield row
            
    def get_headings(self):
        return self._headings
            
    def to_tree(self, id_heading):
        result = pyradox.struct.Tree()
        for row in self._data:
            id_value = row[id_heading]
            if id_value == '': continue
                
            result[id_heading] = pyradox.struct.Tree()
            for heading in self._headings:
                if heading == id_heading: continue
                if heading == '': continue
                value = row[heading]
                if value == '': continue
                result[id_heading][heading] = value
                
        return result

    def to_string(self, spec,
                 table_start, table_end,
                 heading_row_start, heading_row_end, heading_cell_start, heading_cell_end,
                 row_start, row_end, cell_start, cell_end):
        # spec: list of heading_string, cell_spec
        # use heading if heading string is None
        # options for cell spec:
        # * string: format string using row as dictionary
        # * function row -> string
        if spec is None:
            spec = [(heading, '%(' + heading + ')s') for heading in self._headings]
        
        result = table_start

        result += heading_row_start
        for heading_string, cell_spec in spec:
            result += heading_cell_start + heading_string + heading_cell_end
        result += heading_row_end

        for row in self._data:
            result += row_start
            for heading_string, cell_spec in spec:
                if isinstance(cell_spec, str):
                    cell = cell_spec % row
                else:
                    cell = cell_spec(row)
                result += cell_start + cell + cell_end
            result += row_end

        result += table_end
        return result
        
    def to_csv(self, spec = None, separator = ';'):
        return self.to_string(spec,
                            '', '',
                            '', '\n', '', separator,
                            '', '\n', '', separator
                            )

    def to_html(self, spec = None, table_class = 'wikitable sortable'):
        return self.to_string(spec,
                            '<table class="%s">\n' % table_class, '</table>\n',
                            '<tr>', '</tr>\n', '<th>', '</th>',
                            '<tr>', '</tr>\n', '<td>', '</td>'
                            )

    def to_wiki(self, spec = None, table_class = 'wikitable sortable'):
        return self.to_string(spec,
                            '{| class="%s"\n' % table_class, '|}\n',
                            '', '', '! ', ' \n',
                            '|-\n', '', '| ', ' \n'
                            )
