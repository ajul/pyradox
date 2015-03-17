import pyradox.struct

class Table():
    def __init__(self, headings):
        self._headings = headings
        self._data = []

    def makeRow(self, row):
        if hasattr(row, 'items'):
            return {k: v for k, v in row.items()}
        else:
            return {k: v for k, v in zip(self._headings, row)}

    def addRow(self, row):
        self._data.append(self.makeRow(row))
        
    def __iter__(self):
        for row in self._data:
            yield row
            
    def getHeadings(self):
        return self._headings
            
    def toTree(self, idHeading):
        result = pyradox.struct.Tree()
        for row in self._data:
            idValue = row[idHeading]
            if idValue == '': continue
                
            result[idHeading] = pyradox.struct.Tree()
            for heading in self._headings:
                if heading == idHeading: continue
                if heading == '': continue
                value = row[heading]
                if value == '': continue
                result[idHeading][heading] = value
                
        return result

    def toString(self, spec,
                 tableStart, tableEnd,
                 headingRowStart, headingRowEnd, headingCellStart, headingCellEnd,
                 rowStart, rowEnd, cellStart, cellEnd):
        # spec: list of headingString, cellSpec
        # use heading if heading string is None
        # options for cell spec:
        # * string: format string using row as dictionary
        # * function row -> string
        if spec is None:
            spec = [(heading, '%(' + heading + ')s') for heading in self._headings]
        
        result = tableStart

        result += headingRowStart
        for headingString, cellSpec in spec:
            result += headingCellStart + headingString + headingCellEnd
        result += headingRowEnd

        for row in self._data:
            result += rowStart
            for headingString, cellSpec in spec:
                if isinstance(cellSpec, str):
                    cell = cellSpec % row
                else:
                    cell = cellSpec(row)
                result += cellStart + cell + cellEnd
            result += rowEnd

        result += tableEnd
        return result
        
    def toCSV(self, spec = None, separator = ';'):
        return self.toString(spec,
                            '', '',
                            '', '\n', '', separator,
                            '', '\n', '', separator
                            )

    def toHTML(self, spec = None, tableClass = 'wikitable sortable'):
        return self.toString(spec,
                            '<table class="%s">\n' % tableClass, '</table>\n',
                            '<tr>', '</tr>\n', '<th>', '</th>',
                            '<tr>', '</tr>\n', '<td>', '</td>'
                            )

    def toWiki(self, spec = None, tableClass = 'wikitable sortable'):
        return self.toString(spec,
                            '{| class="%s"\n' % tableClass, '|}\n',
                            '', '', '! ', ' \n',
                            '|-\n', '', '| ', ' \n'
                            )
