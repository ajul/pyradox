import traceback

import io
import re
import os
import sys
import zipfile

sys.path.append("../..")
import pyradox.primitive
import pyradox.table
import pyradox.txt

war_headings = [
    'war_name',
    'start_year', 'start_month', 'start_day',
    'end_year', 'end_month', 'end_day',
    'number_of_battles',
    'country', 'side', 'is_war_leader',
    'friendly_losses', 'enemy_losses',
    ]

battle_headings = [
    'war_name', 'battle_name',
    'year', 'month', 'day',
    'country', 'enemy', 'side', 'won',
    'type', # land or naval
    'friendly_leader', 'enemy_leader',
    'friendly_strength', 'enemy_strength',
    'friendly_losses', 'enemy_losses',
    ]

ship_words = ['ship', 'transport', 'galley', 'commerce_raider', 'cruiser', 'dreadnought', 'frigate', 'ironclad', 'man_o_war', 'monitor']

def is_naval(battle_data):
    for key in (battle_data['attacker'] + battle_data['defender']).keys():
        if any(word in key for word in ship_words): return True
    return False

def find_belligerents(war_data):
    # return country, side, is_war_leader
    found_attacker_war_leader = False
    found_defender_war_leader = False

    for date, events in war_data['history'].items():
        if not isinstance(date, pyradox.primitive.Date): continue
        for key, value in events.items():
            if key == 'add_attacker':
                yield value, 'attacker', not found_attacker_war_leader
                found_attacker_war_leader = True
            elif key == 'add_defender':
                yield value, 'defender', not found_defender_war_leader
                found_defender_war_leader = True

def find_war_start_date(war_data):
    for date, events in war_data['history'].items():
        if isinstance(date, pyradox.primitive.Date): return date

def find_war_end_date(war_data):
    for date in reversed([x for x in war_data['history'].keys()]):
        if isinstance(date, pyradox.primitive.Date): return date

def find_strength(side_data):
    return sum(value for key, value in side_data.items() if isinstance(value, int) and key not in ('losses',))

def process_battle(battle_table, war_losses, war_name, date, battle_data):
    if date is None:
        year, month, day = '', '', ''
    else:
        year, month, day = date.year, date.month, date.day

    attacker_data = battle_data['attacker']
    defender_data = battle_data['defender']

    war_losses[0] += attacker_data['losses']
    war_losses[1] += defender_data['losses']

    battle_table.add_row({
        'war_name' : war_name,
        'battle_name' : battle_data['name'] or '',
        'year' : year,
        'month' : month,
        'day' : day,
        'country' : attacker_data['country'] or '',
        'enemy' : defender_data['country'] or '',
        'side' : 'attacker',
        'won' : battle_data['result'],
        'type' : 'naval' if is_naval(battle_data) else 'land', # land or naval
        'friendly_leader' : attacker_data['commander'] or attacker_data['leader'] or '',
        'enemy_leader' : defender_data['commander'] or defender_data['leader'] or '',
        'friendly_strength' : find_strength(attacker_data),
        'enemy_strength' : find_strength(defender_data),
        'friendly_losses' : attacker_data['losses'],
        'enemy_losses' : defender_data['losses'],
    })

    battle_table.add_row({
        'war_name' : war_name,
        'battle_name' : battle_data['name'] or '',
        'year' : year,
        'month' : month,
        'day' : day,
        'country' : defender_data['country'] or '',
        'enemy' : attacker_data['country'] or '',
        'side' : 'defender',
        'won' : not battle_data['result'],
        'type' : 'naval' if is_naval(battle_data) else 'land', # land or naval
        'friendly_leader' : defender_data['commander'] or defender_data['leader'] or '', 
        'enemy_leader' : attacker_data['commander'] or attacker_data['leader'] or '',
        'friendly_strength' : find_strength(defender_data),
        'enemy_strength' : find_strength(attacker_data),
        'friendly_losses' : defender_data['losses'],
        'enemy_losses' : attacker_data['losses'],
    })

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
    m = re.search('(^(active|previous)_war\s*=.*?)^(?=\w+)(?!(active|previous)_war)', data, flags = re.DOTALL | re.MULTILINE)
    if m is None:
        raise Exception("War data not found.")

    data = pyradox.txt.parse(m.group(1), filename=in_filename)

    war_table = pyradox.table.Table(war_headings)
    battle_table = pyradox.table.Table(battle_headings)

    for war_type, war_data in data.items():
        war_name = war_data['name']

        start_date = find_war_start_date(war_data)
        if start_date is None:
            start_year, start_month, start_day = '', '', ''
        else:
            start_year, start_month, start_day = start_date.year, start_date.month, start_date.day
        if war_type == 'active_war':
            end_year = 'present'
            end_month = 'present'
            end_day = 'present'
        else:
            end_date = find_war_end_date(war_data)
            if end_date is None:
                end_year, end_month, end_day = '', '', ''
            else:
                end_year, end_month, end_day = end_date.year, end_date.month, end_date.day

        war_losses = [0, 0]
        num_battles = 0

        for date, events in war_data['history'].items():
            if isinstance(date, pyradox.primitive.Date):
                for event_type, battle_data in events.items():
                    if event_type == 'battle':
                        process_battle(battle_table, war_losses, war_name, date, battle_data)
                        num_battles += 1
            else:
                if date == 'battle':
                    process_battle(battle_table, war_losses, war_name, start_date, events)
                    num_battles += 1

        for country, side, is_war_leader in find_belligerents(war_data):
            war_table.add_row({
                'war_name' : war_name,
                'start_year' : start_year,
                'start_month' : start_month,
                'start_day' : start_day,
                'end_year' : end_year,
                'end_month' : end_month,
                'end_day' : end_day,
                'number_of_battles' : num_battles,
                'country' : country,
                'side' : side,
                'is_war_leader' : is_war_leader,
                'friendly_losses' : war_losses[0] if side == 'attacker' else war_losses[1],
                'enemy_losses' : war_losses[0] if side == 'defender' else war_losses[1],
                })

    out_war_file = open(out_filename_base + '.war.csv', mode='w', encoding=pyradox.txt.encoding)
    out_war_file.write(war_table.to_csv(separator=','))
    out_war_file.close()

    out_battle_file = open(out_filename_base + '.battle.csv', mode='w', encoding=pyradox.txt.encoding)
    out_battle_file.write(battle_table.to_csv(separator=','))
    out_battle_file.close()

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
                
                
