import _initpath
import os
import re
import sys
import pyradox
import time

def parse_walk(dirname, verbose=False):
    """Given a directory, recursively iterate over the content of the .txt files in that directory as Trees"""
    
skip = '\\\\(map|wiki|interface|pdx_launcher|previewer_assets)\\\\'

start_time = time.clock()

file_count = 0

dirname = os.path.join(pyradox.get_game_directory('HoI4'))
for root, dirs, files in os.walk(dirname):
    if root == dirname: continue
    for filename in files:
        fullpath = os.path.join(root, filename)
        _, ext = os.path.splitext(fullpath)
        if ext == ".txt" and not re.search(skip, fullpath):
            try:
                pyradox.parse_file(fullpath)
                file_count += 1
            except:
                print(sys.exc_info())
end_time = time.clock()

print("Parsed %d files in %0.1fs" % (file_count, end_time - start_time))
