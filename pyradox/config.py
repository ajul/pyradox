import errno
import os
from glob import glob

language = 'english'

# If you know the location of your games but it is not being found automatically, add it to the top of this list.
# Uses glob, but not recursively (no **).
_prefixes = [
    r'/Program Files*/Steam/steamapps/common/',
    r'~/Library/Application Support/Steam/steamapps/common/',
]

_game_directories = {
    'EU4' : r'Europa Universalis IV',
    'HoI3' : r'Hearts of Iron 3/tfh',
    'HoI3_vanilla' : r'Hearts of Iron 3',
    'HoI4' : r'Hearts of Iron IV',
    'HoI4_beta' : r'Hearts of Iron IV BETA', 
    'Stellaris' : r'Stellaris',
}

_basedirs = {}

_default_game = None

def set_default_game(game):
    global _default_game
    _default_game = game

def get_default_game():
    if _default_game is None:
        raise RuntimeError('Default game not set!')
    return _default_game
    
def get_basedir(game = None):
    if game is None: game = get_default_game()
    if game not in _basedirs:
        # search for game
        game_directory = _game_directories[game]
        
        for prefix in _prefixes:
            pattern = os.path.join(prefix, game_directory)
            candidates = glob(pattern)
            if len(candidates) > 0:
                _basedirs[game] = candidates[0]
                break
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), game_directory)
    return _basedirs[game]
