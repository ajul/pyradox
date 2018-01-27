import pyradox

def get_units(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    return pyradox.parse_merge('common/units', game = game, merge_levels = 1)['sub_units']

def get_technologies(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    return pyradox.parse_merge('common/technologies', game = game, merge_levels = 1)['technologies']

def get_equipments(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    return pyradox.parse_merge('common/units/equipment', game = game, merge_levels = 1)['equipments']