import hoi4
import pyradox

date = '1936.1.1'

states = hoi4.load.get_states()
countries = hoi4.load.get_countries(date = date)



def get_state_name(state_id):
    state = states[state_id]
    return pyradox.yml.get_localisation(state['name'], game = 'HoI4')

def get_state_owner(state_id):
    state = states[state_id]
    history = state['history'].at_time(date, merge_levels = -1)
    return countries[history['owner']]