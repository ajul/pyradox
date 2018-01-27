import pyradox

import copy
import os


# helper functions for loading directory contents 

cache = {}

def load_functions(game, name, dirpath, mode = None, merge_levels = 0):
    if isinstance(dirpath, str): dirpath = (dirpath,)
    def parse_data(basedir = None):
        if basedir is None: basedir = pyradox.get_game_directory(game)

        if mode == "merge":
            result = pyradox.parse_merge(os.path.join(basedir, *dirpath), merge_levels = merge_levels)
        elif mode == "walk":
            result = pyradox.Tree()
            for filename, tree in pyradox.parse_walk(os.path.join(basedir, *dirpath)):
                tag, raw_name = pyradox.format.split_filename(filename)
                result.append(tag, tree)
        else:
            result = pyradox.Tree()
            for filename, tree in pyradox.parse_dir(os.path.join(basedir, *dirpath)):
                tag, raw_name = pyradox.format.split_filename(filename)
                result.append(tag, tree)
            
        print('Loaded %s.' % name)
        return result

    def get_data(basedir = None):
        if basedir is None: basedir = pyradox.get_game_directory(game)
        if basedir not in cache: cache[basedir] = {}
        if name not in cache[basedir]: cache[basedir][name] = parse_data(basedir)
        return copy.deepcopy(cache[basedir][name])

    return parse_data, get_data
