import _initpath
import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml

def getStabilityLikely(conditions):
    result = [0 for x in range(7)]
    
    for stability in conditions.findAll("stability"):
        result[stability] = 1

    for notCondition in conditions.findAll("NOT"):
        for stability in notCondition.findAll("stability"):
            result[stability] = -1

    return result

eventsTree = pyradox.txt.parseFile(os.path.join(pyradox.config.basedirs['EU4'], 'events', 'Republics.txt'))

allowEvents = list(list([] for x in range(3)) for x in range(7))
likelyEvents = list(list([] for x in range(3)) for x in range(7))

for event in eventsTree.findAll("country_event"):
    eventName = pyradox.yml.getLocalization(event["title"], sources = ['generic_events'])
    if "trigger" in event:
        allow = getStabilityLikely(event["trigger"])
        for i, x in enumerate(allow):
            if eventName not in allowEvents[i][x]:
                allowEvents[i][x].append(eventName)
        
    if "mean_time_to_happen" in event:
        likelies = [0] * 7
        for modifier in event["mean_time_to_happen"].findAll("modifier"):
            if modifier["factor"] > 1.0:
                sign = 1
            else:
                sign = -1

            for i, likely in enumerate(getStabilityLikely(modifier)):
                likelies[i] += sign * likely

        for i, x in enumerate(likelies):
            if eventName not in likelyEvents[i][x]:
                likelyEvents[i][x].append(eventName)

s = '{|class = "wikitable"\n'
s += '! Stability !! Enabled !! More likely !! Less likely !! Disabled\n'
for i in range(-3, 4):
    s += "|-\n"

    s += '! %d \n' % i
    
    s += "| \n"
    for event in allowEvents[i][1]:
        s += "* [[Republic events#%s|%s]] \n" % (event, event)

    s += "| \n"
    for event in likelyEvents[i][1]:
        s += "* [[Republic events#%s|%s]] \n" % (event, event)

    s += "| \n"
    for event in likelyEvents[i][-1]:
        s += "* [[Republic events#%s|%s]] \n" % (event, event)
    
    s += "| \n"
    for event in allowEvents[i][-1]:
        s += "* [[Republic events#%s|%s]] \n" % (event, event)

s += "|}\n"

print(s)
