import _initpath
import re
import copy

import pyradox.hoi4.tech
import json

defaultYear = 1918

techs = pyradox.hoi4.tech.getTechs()["technologies"]

#
# folders = [ "land_doctrine_folder","naval_doctrine_folder","air_doctrine_folder" ]
folders = [ "land_doctrine_folder" ]

data = techs.rawData();

techPaths = {};

children = {};
parents = {};
doctrines = {};
#xor = {}; # don't need any branching is always xor?????

for folder in folders :
    doctrines[folder] = {};
    techPaths[folder] = {};
    for techKey in data :
        tech=data[techKey]
        if(type(tech) is dict):
            if( 'folder' in tech):
                techFolder = tech["folder"]
                isDoctrine = False
                if(type(techFolder) is dict):
                    if techFolder["name"] == folder :
                        isDoctrine = True
                #else :
                    #Skipping there are no doctrines in multiple folders
                if(isDoctrine) :
                    doctrines[folder][techKey] = tech
                    if( 'path' in tech ):
                        if(not techKey in children):
                            children[techKey] = {}
                        paths = tech["path"];
                        if(type(paths) is dict):
                            paths = [paths]
                        for path in paths :
                            children[techKey][path["leads_to_tech"]] = 1
                            parents[path["leads_to_tech"]] = techKey


output = {};

ignore = {
    "path" : 1,
    "ai_will_do" : 1,
    "doctrine" : 1,
    "folder" : 1,
    "ai_research_weights" : 1,
    "categories" : 1,
    "xor" : 1,
}

def processNode(counter,doctrine,techKey,path,effects) :
    tech = doctrines[doctrine][techKey];
    for key in tech :
        if(not key in ignore):
            if(not key in effects):
                effects[key] = None;
            effects[key] = merge(effects[key],tech[key])
    if(not counter in output[doctrine]):
        output[doctrine][counter] = []
    output[doctrine][counter].append([path,effects])
    if(techKey in children) :
        for child in children[techKey]:
#             if(not "xor" in doctrines[doctrine][child] and ( len(children[techKey]) > 1 )   ) :
                #If we are not in xor mode (naval doctrine) we want to gather all things on same level and merge
#                print(child)
#            else :
                newPath = copy.deepcopy(path)
                newEffects = copy.deepcopy(effects)
                if(len(children[techKey]) > 1):
                    newPath.append(child)
                processNode(counter+1,doctrine,child,newPath,newEffects)

def merge(existing,new):
    newType = type(new)
    existingType = type(existing)
    if(newType is int or newType is float) :
        if(existing is None):
            existing = 0
        return existing+new
    elif(newType is list):
        if(existing is None):
            existing = []
        for value in new :
            existing.append(value)
        return existing
    elif(newType is str):
        if(existing is None):
            existing = []
        existing.append(new);
        return existing;
    elif(newType is dict):
        if(existing is None):
            existing = {}
        for key in new :
            if(not key in existing):
                existing[key] = None;
            existing[key] = merge(existing[key],new[key])
        return existing
    else :
        print(newType,new)

    return None



for doctrine in doctrines :
    output[doctrine] = {};
    for techKey in doctrines[doctrine] :
        if(not techKey in parents):
            #Lets start down this tree
            processNode(0,doctrine,techKey,[techKey],{})

print(json.dumps(output["land_doctrine_folder"][4],indent=2,sort_keys=True))