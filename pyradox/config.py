_basedirs = {
    'EU4' : r'C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV',
    'HoI3' : r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron 3\tfh',
    'HoI3_vanilla' : r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron 3',
    'HoI4_beta' : r'C:\Program Files (x86)\Steam\SteamApps\common\Hearts of Iron IV BETA',
    'HoI4' : r'C:\Program Files (x86)\Steam\SteamApps\common\Hearts of Iron IV',
    }

language = 'english'

_defaultGame = None

def setDefaultGame(game):
    global _defaultGame
    _defaultGame = game

def getDefaultGame():
    if _defaultGame is None:
        raise RuntimeError('Default game not set!')
    return _defaultGame
    
def getBasedir(game = None):
    if game is None: return _basedirs[getDefaultGame()]
    return _basedirs[game]
