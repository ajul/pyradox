import _initpath
import os
import pyradox.config
import pyradox.format

import pyradox
import pyradox.yml

def get_stability_likely(conditions):
    result = [0 for x in range(7)]
    
    for stability in conditions.find_all("stability"):
        result[stability] = 1

    for not_condition in conditions.find_all("NOT"):
        for stability in not_condition.find_all("stability"):
            result[stability] = -1

    return result

events_tree = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('EU4'), 'events', 'Republics.txt'))

allow_events = list(list([] for x in range(3)) for x in range(7))
likely_events = list(list([] for x in range(3)) for x in range(7))

for event in events_tree.find_all("country_event"):
    event_name = pyradox.yml.get_localization(event["title"], sources = ['generic_events'])
    if "trigger" in event:
        allow = get_stability_likely(event["trigger"])
        for i, x in enumerate(allow):
            if event_name not in allow_events[i][x]:
                allow_events[i][x].append(event_name)
        
    if "mean_time_to_happen" in event:
        likelies = [0] * 7
        for modifier in event["mean_time_to_happen"].find_all("modifier"):
            if modifier["factor"] > 1.0:
                sign = 1
            else:
                sign = -1

            for i, likely in enumerate(get_stability_likely(modifier)):
                likelies[i] += sign * likely

        for i, x in enumerate(likelies):
            if event_name not in likely_events[i][x]:
                likely_events[i][x].append(event_name)

s = '{|class = "wikitable"\n'
s += '! Stability !! Enabled !! More likely !! Less likely !! Disabled\n'
for i in range(-3, 4):
    s += "|-\n"

    s += '! %d \n' % i
    
    s += "| \n"
    for event in allow_events[i][1]:
        s += "* [[Republic events#%s|%s]] \n" % (event, event)

    s += "| \n"
    for event in likely_events[i][1]:
        s += "* [[Republic events#%s|%s]] \n" % (event, event)

    s += "| \n"
    for event in likely_events[i][-1]:
        s += "* [[Republic events#%s|%s]] \n" % (event, event)
    
    s += "| \n"
    for event in allow_events[i][-1]:
        s += "* [[Republic events#%s|%s]] \n" % (event, event)

s += "|}\n"

print(s)
