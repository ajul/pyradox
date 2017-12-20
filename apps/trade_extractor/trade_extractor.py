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

trade_headings = [
    'node',
    'country',
    'power',
    'money',
    ]

def extract(in_filename, out_filename_base = None):
    if out_filename_base is None:
        out_filename_base = in_file_name
    
    # open and read the save
    if zipfile.is_zipfile(in_filename):
        in_file = zipfile.ZipFile(in_filename)
        for info in in_file.infolist():
            if info.filename != 'meta':
                data = in_file.read(info).decode(pyradox.txt.encoding)
        in_file.close()
    else:
        in_file = open(in_filename, encoding=pyradox.txt.encoding)
        data = in_file.read()
        in_file.close()

    # excerpt the relevant section
    m = re.search('trade=.*?(?=production_leader_tag)', data, flags = re.DOTALL | re.MULTILINE)
    if m is None:
        raise Exception("Trade data not found.")

    data = pyradox.txt.parse(m.group(0), filename=in_filename)
    trade_data = data['trade']

    trade_table = pyradox.table.Table(trade_headings)

    for node_data in trade_data.values():
        node = node_data['definitions']
        for country, country_data in node_data.items():
            if isinstance(country_data, pyradox.struct.Tree):
                if 'type' not in country_data: continue
                money = country_data['money'] or 0.0
                power = country_data['max_pow'] or 0.0
                trade_table.add_row({
                    'node' : node,
                    'country' : country,
                    'power' : power,
                    'money' : money,
                    })

    out_trade_file = open(out_filename_base + '.trade.csv', mode='w', encoding=pyradox.txt.encoding)
    out_trade_file.write(trade_table.to_csv(separator=','))
    out_trade_file.close()

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
            in_filename = os.path.join(dirname, filename)
            out_filename_base = os.path.join('out', filename)
            if os.path.isfile(in_filename):
                try:
                    extract(in_filename, out_filename_base)
                except:
                    print('Failed to extract data from %s.' % in_filename)
                    traceback.print_exc()
                else:
                    print('Extracted data from %s and written to %s.' % (in_filename, out_filename_base))
                
                
