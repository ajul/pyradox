import errno
import os
from glob import glob

language = 'english'

# If you know the location of your games but it is not being found automatically, add it to the top of this list.
# Uses glob, but not recursively (no **).
prefixes = [
    r'/Program Files*/Steam/steamapps/common/', # windows
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

default_game = None

def get_language():
    return language

def set_default_game(game):
    global default_game
    default_game = game

def get_default_game():
    if default_game is None:
        raise RuntimeError('Default game not set!')
    return default_game
    
def get_game_directory(game = None):
    if game is None: game = get_default_game()
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
