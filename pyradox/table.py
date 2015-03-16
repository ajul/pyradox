import pyradox.struct

class Table():
    def __init__(self, headings):
        self._headings = headings
        self._data = []

    def makeRow(self, row):
        if hasattr(row, 'items'):
            result = [''] * len(self._headings)
            for key, value in row.items():
                result[getHeadingIndex(key)] = value
            return result
        else:
            return row

    def addRow(self, row):
        self._data.append(self.makeRow(row))
        
    def __iter__(self):
        for row in self._data:
            yield row
            
    def getHeadings(self):
        return self._headings
            
    def getHeadingIndex(self, heading):
        if isinstance(heading, int):
            return heading
        elif isinstance(heading, str):
            return self._headings.index(heading.lower())
            
    def selectColumns(self, headings):
        headingIndexes = [self.getHeadingIndex(heading) for heading in headings]
                
        for row in self._data:
            yield [row[index] for index in headingIndexes]
            
    def toTree(self, idHeading = 0):
        result = pyradox.struct.Tree()
        idHeadingIndex = self.getHeadingIndex(idHeading)
        for row in self._data:
            idValue = row[idHeadingIndex]
            if idValue == '': continue
                
            result[idValue] = pyradox.struct.Tree()
            for i, heading in enumerate(self._headings):
                if i == idHeadingIndex: continue
                if heading == '': continue
                value = row[i]
                if value == '': continue
                result[idValue][heading] = value
                
        return result

    def toString(self, spec,
                 tableStart, tableEnd,
                 headingRowStart, headingRowEnd, headingCellStart, headingCellEnd,
                 rowStart, rowEnd, cellStart, cellEnd):
    
        # spec: list of (heading, (heading string, cell spec))
        # use heading if heading string is None
        # options for cell spec:
        # * None: output str(value)
        # * string: format string with one replacement
        result = tableStart

        result += headingRowStart
        for heading, (headingString, cellSpec) in spec:
            if headingString is None:
                headingString = heading
            result += headingCellStart + headingString + headingCellEnd
        result += headingRowEnd

        for row in self._data:
            result += rowStart
            for heading, (headingString, cellSpec) in spec:
                value = row[self.getHeadingIndex(heading)]
                if cellSpec is None:
                    cellSpec = '%s'
                cell = cellSpec % value
                result += cellStart + cell + cellEnd
            result += rowEnd

        result += tableEnd
        return result

    def toHTML(self, spec, tableClass = 'wikitable sortable'):
        return self.toString(spec,
                            '<table class="%s">\n' % tableClass, '</table>\n',
                            '<tr>', '</tr>\n', '<th>', '</th>',
                            '<tr>', '</tr>\n', '<td>', '</td>'
                            )

    def toWiki(self, spec, tableClass = 'wikitable sortable'):
        return self.toString(spec,
                            '{| class="%s"\n' % tableClass, '|}\n',
                            '', '', '! ', ' \n',
                            '|-\n', '', '| ', ' \n'
                            )
