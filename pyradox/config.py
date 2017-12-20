_basedirs = {
    'EU4' : r'C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV',
    'HoI3' : r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron 3\tfh',
    'HoI3_vanilla' : r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron 3',
    'HoI4_beta' : r'C:\Program Files (x86)\Steam\SteamApps\common\Hearts of Iron IV BETA',
    'HoI4' : r'C:\Program Files (x86)\Steam\SteamApps\common\Hearts of Iron IV',
    'Stellaris' : r'C:\Program Files (x86)\Steam\SteamApps\common\Stellaris',
    }

language = 'english'

_default_game = None

def set_default_game(game):
    global _default_game
    _default_game = game

def get_default_game():
    if _default_game is None:
        raise RuntimeError('Default game not set!')
    return _default_game
    
def get_basedir(game = None):
    if game is None: return _basedirs[get_default_game()]
    return _basedirs[game]
