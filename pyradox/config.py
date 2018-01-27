import errno
import os
from glob import glob

language = 'english'

# If you know the location of your games but it is not being found automatically, add it to the top of this list.
# Uses glob, but not recursively (no **).
prefixes = [
    r'/Program Files*/Steam/steamapps/common/', # windows
    r'/Steam/steamapps/common/',
    r'~/Library/Application Support/Steam/steamapps/common/', # mac
    r'~/*steam/steam/SteamApps/common', # linux
]

game_suffixes = {
    'EU4' : r'Europa Universalis IV',
    'HoI3' : r'Hearts of Iron 3/tfh',
    'HoI3_vanilla' : r'Hearts of Iron 3',
    'HoI4' : r'Hearts of Iron IV',
    'HoI4_beta' : r'Hearts of Iron IV BETA', 
    'Stellaris' : r'Stellaris',
}

game_directories = {}

def get_language():
    return language

def path_to_list(path):
    return os.path.normpath(path).split(os.sep)
    
def is_subpath(subpath, path):
    subpath = path_to_list(subpath)
    path = path_to_list(path)
    
    for i in range(len(path)):
        if subpath == path[i:i+len(subpath)]:
            return True
    
    return False
    
def get_game_from_path(path):
    for game, game_suffix in game_suffixes.items():
        if is_subpath(game_suffix, path):
            return game
    raise KeyError('Could not find game corresponding to path "%s".' % path)
    
def get_game_directory(game):
    if game not in game_directories:
        # search for game
        game_suffix = game_suffixes[game]
        
        for prefix in prefixes:
            pattern = os.path.join(prefix, game_suffix)
            candidates = glob(pattern)
            if len(candidates) > 0:
                game_directories[game] = candidates[0]
                break
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), game_suffix)
    return game_directories[game]

def combine_path_and_game(path, game = None):
    """
    Determines the absolute path and game from each other.
    
    path: A string, or a sequence of path components which will be joined.
    
    If game is None, path is a full path and the game is determined from that.
    Or game can be supplied, in which case path can be a path relative to the game directory.
    """
    
    try:
        path = os.fspath(path)
    except:
        if not isinstance(path, (str, bytes)):
            path = os.path.join(*path)
    
    if game is None:
        path = os.path.abspath(path)
        game = get_game_from_path(path)
    elif not os.path.isabs(path):
        path = os.path.join(get_game_directory(game), path)
    return path, game