import pyradox

slot_sizes = {
    'small' : 1,
    'point_defence' : 1,
    'medium' : 2,
    'torpedo' : 2,
    'large' : 4,
    'hangar' : 4,
    'extra_large' : 8,
    'titanic' : 16, #?
    'planet_killer' : 1,
    }

slot_icons = {
    'small' : 's',
    'point_defence' : 'pd',
    'medium' : 'm',
    'torpedo' : 'g',
    'large' : 'l',
    'hangar' : 'h',
    'extra_large' : 'xl',
    'titanic' : 't',
    'planet_killer' : 'wd',
    }

def average_damage(weapon):
    if 'damage' in weapon:
        min_damage = weapon['damage']['min']
        max_damage = weapon['damage']['max']
    else:
        min_damage = weapon['min_damage']
        max_damage = weapon['max_damage']
    
    return 0.5 * (min_damage + max_damage)

def normalized_dps(weapon):
    if 'count' in weapon:
        count = weapon['count']
    else:
        count = 1
        
    dps_per_size = count * average_damage(weapon) / weapon['cooldown'] / slot_sizes[weapon['size'].lower()]
    
    effectiveness_numerator = (
        0.5 * weapon['hull_damage'] +
        0.25 * weapon['armor_damage'] * (1.0 - weapon['armor_penetration']) +
        0.25 * weapon['shield_damage'] * (1.0 - weapon['shield_penetration']))
    
    effectiveness_denominator = 0.5 + 0.25 * (1.0 - weapon['armor_penetration']) + 0.25 * (1.0 - weapon['shield_penetration'])
    
    accuracy_mult = weapon['accuracy']
    result = dps_per_size * accuracy_mult * effectiveness_numerator / effectiveness_denominator / effectiveness_denominator
    return result

def float_to_255(x):
    x = round(255.0 * x)
    return max(min(x, 255), 0)

def to_html_color(c):
    return '#%02x%02x%02x' % c

def special_color(key, weapon):
    if weapon['armor_penetration'] == 1.0 and weapon['shield_penetration'] == 1.0:
        r = 1.0
        g = 0.0
        b = 1.0
    else:
        hull = 1.0
        armor = weapon['armor_damage'] / weapon['hull_damage']
        shield = weapon['shield_damage'] / weapon['hull_damage']
        
        non_penetrating = [hull]
        if weapon['armor_penetration'] < 1.0:
            non_penetrating.append(armor)
        if weapon['shield_penetration'] < 1.0:
            non_penetrating.append(shield)

        m = max(non_penetrating)

        power = 2.0

        if weapon['armor_penetration'] < 1.0:
            r = 0.5 * (armor / m) ** power
        else:
            r = 1.0
        g = 0.5 * (hull / m) ** power
        if weapon['shield_penetration'] < 1.0:
            b = 0.5 * (shield / m) ** power
        else:
            b = 1.0

    c = (float_to_255(r), float_to_255(g), float_to_255(b))
    return to_html_color(c)

def special_description(key, weapon):
    hull = weapon['hull_damage']
    armor = weapon['armor_damage']
    shield = weapon['shield_damage']

    ap = weapon['armor_penetration']
    sp = weapon['shield_penetration']

    if ap == 1.0 and sp == 1.0:
        text = 'penetrating'
    elif ap == 1.0:
        text = 'armor-penetrating'
    elif sp == 1.0:
        text = 'shield-penetrating'
    elif hull > armor and hull > shield:
        text = 'anti-hull'
    elif armor > hull and armor > shield:
        text = 'anti-armor'
    elif shield > hull and shield > armor:
        text = 'anti-shield'
    else:
        return ''

    color = special_color(key, weapon)

    result = ''
    result += '<p style="color:%s; font-weight:bold; text-align:right; margin:0;">%s</p>' % (color, text)
    return result
    
def special_string(key, weapon):
    #items = [special_description(key, weapon)]
    items = []

    if weapon['hull_damage'] != 1.0:
        items.append('%d%% hull damage' % (weapon['hull_damage'] * 100.0))

    if weapon['armor_damage'] != 1.0:
        items.append('%d%% armor damage' % (weapon['armor_damage'] * 100.0))

    if weapon['armor_penetration'] != 0.0:
        items.append('%d%% armor penetration' % (weapon['armor_penetration'] * 100.0))
    
    if weapon['shield_damage'] != 1.0:
        items.append('%d%% shield damage' % (weapon['shield_damage'] * 100.0))

    if weapon['shield_penetration'] != 0.0:
        items.append('%d%% shield penetration' % (weapon['shield_penetration'] * 100.0))
    
    result = '<br/>'.join(items)
    
    if len(items) > 2:
        percent = 200.0 / len(items)
        result = '<span style="font-size:%d%%;">%s</span>' % (percent, result)
    
    return result
    
def is_missile(key, weapon):
    return weapon['missile_health'] > 0.0

def slot_string(key, weapon):
    return '{{icon|slot %s}}' % slot_icons[weapon['size'].lower()]

def icon_and_name(k, v):
    tech = v['prerequisites'].replace('_', ' ')
    name = pyradox.get_localisation(k, game = 'Stellaris')

    return '[[File:%s.png|26px]] %s' % (tech, name)
    
def icon_and_name_and_role(k, v):
    line_0 = icon_and_name(k, v)
    line_1 = special_description(k, v)
    
    if line_1 == '': return line_0
    else:
        return '%s<br/>%s' % (line_0, line_1)
    
def weapon_category(key, weapon):
    if weapon['type'] == 'instant': return weapon['tags'] or 'none'
    else: return weapon['type'] or 'none'
    
def sort_function(key, weapon):
    component_set = weapon['prerequisites'] or key
    return component_set, slot_sizes[weapon['size'].lower()]
