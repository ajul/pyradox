import traceback

import io
import re
import os
import sys
import zipfile

sys.path.append("../..")
import pyradox.primitive
import pyradox.struct
import pyradox.table
import pyradox.txt

tradeHeadings = [
    'node',
    'country',
    'power',
    'money',
    ]

def extract(inFilename, outFilenameBase = None):
    if outFilenameBase is None:
        outFilenameBase = inFileName
    
    # open and read the save
    if zipfile.is_zipfile(inFilename):
        inFile = zipfile.ZipFile(inFilename)
        for info in inFile.infolist():
            if info.filename != 'meta':
                data = inFile.read(info).decode(pyradox.txt.encoding)
        inFile.close()
    else:
        inFile = open(inFilename, encoding=pyradox.txt.encoding)
        data = inFile.read()
        inFile.close()

    # excerpt the relevant section
    m = re.search('trade=.*?(?=production_leader_tag)', data, flags = re.DOTALL | re.MULTILINE)
    if m is None:
        raise Exception("Trade data not found.")

    data = pyradox.txt.parse(m.group(0), filename=inFilename)
    tradeData = data['trade']

    tradeTable = pyradox.table.Table(tradeHeadings)

    for nodeData in tradeData.values():
        node = nodeData['definitions']
        for country, countryData in nodeData.items():
            if isinstance(countryData, pyradox.struct.Tree):
                if 'type' not in countryData: continue
                money = countryData['money'] or 0.0
                power = countryData['max_pow'] or 0.0
                tradeTable.addRow({
                    'node' : node,
                    'country' : country,
                    'power' : power,
                    'money' : money,
                    })

    outTradeFile = open(outFilenameBase + '.trade.csv', mode='w', encoding=pyradox.txt.encoding)
    outTradeFile.write(tradeTable.toCSV(separator=','))
    outTradeFile.close()

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        # explicit input and output files
        extract(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        # put output file at same place as input
        extract(sys.argv[1])
    else:
        # use in/ and out/ dirs
        dirname = 'in'
        for filename in os.listdir(dirname):
            inFilename = os.path.join(dirname, filename)
            outFilenameBase = os.path.join('out', filename)
            if os.path.isfile(inFilename):
                try:
                    extract(inFilename, outFilenameBase)
                except:
                    print('Failed to extract data from %s.' % inFilename)
                    traceback.print_exc()
                else:
                    print('Extracted data from %s and written to %s.' % (inFilename, outFilenameBase))
                
                
