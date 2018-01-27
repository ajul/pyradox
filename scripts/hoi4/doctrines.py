import hoi4
import re
import copy

import hoi4
import json

default_year = 1918

techs = hoi4.load.get_technologies()

#
# folders = [ "land_doctrine_folder","naval_doctrine_folder","air_doctrine_folder" ]
folders = [ "land_doctrine_folder" ]

data = techs.raw_data();

tech_paths = {};

children = {};
parents = {};
doctrines = {};
#xor = {}; # don't need any branching is always xor?????

for folder in folders :
    doctrines[folder] = {};
    tech_paths[folder] = {};
    for tech_key in data :
        tech=data[tech_key]
        if(type(tech) is dict):
            if( 'folder' in tech):
                tech_folder = tech["folder"]
                is_doctrine = False
                if(type(tech_folder) is dict):
                    if tech_folder["name"] == folder :
                        is_doctrine = True
                #else :
                    #Skipping there are no doctrines in multiple folders
                if(is_doctrine) :
                    doctrines[folder][tech_key] = tech
                    if( 'path' in tech ):
                        if(not tech_key in children):
                            children[tech_key] = {}
                        paths = tech["path"];
                        if(type(paths) is dict):
                            paths = [paths]
                        for path in paths :
                            children[tech_key][path["leads_to_tech"]] = 1
                            parents[path["leads_to_tech"]] = tech_key


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

def process_node(counter,doctrine,tech_key,path,effects) :
    tech = doctrines[doctrine][tech_key];
    for key in tech :
        if(not key in ignore):
            if(not key in effects):
                effects[key] = None;
            effects[key] = merge(effects[key],tech[key])
    if(not counter in output[doctrine]):
        output[doctrine][counter] = []
    output[doctrine][counter].append([path,effects])
    if(tech_key in children) :
        for child in children[tech_key]:
#             if(not "xor" in doctrines[doctrine][child] and ( len(children[tech_key]) > 1 )   ) :
                #If we are not in xor mode (naval doctrine) we want to gather all things on same level and merge
#                print(child)
#            else :
                new_path = copy.deepcopy(path)
                new_effects = copy.deepcopy(effects)
                if(len(children[tech_key]) > 1):
                    new_path.append(child)
                process_node(counter+1,doctrine,child,new_path,new_effects)

def merge(existing,new):
    new_type = type(new)
    existing_type = type(existing)
    if(new_type is int or new_type is float) :
        if(existing is None):
            existing = 0
        return existing+new
    elif(new_type is list):
        if(existing is None):
            existing = []
        for value in new :
            existing.append(value)
        return existing
    elif(new_type is str):
        if(existing is None):
            existing = []
        existing.append(new);
        return existing;
    elif(new_type is dict):
        if(existing is None):
            existing = {}
        for key in new :
            if(not key in existing):
                existing[key] = None;
            existing[key] = merge(existing[key],new[key])
        return existing
    else :
        print(new_type,new)

    return None



for doctrine in doctrines :
    output[doctrine] = {};
    for tech_key in doctrines[doctrine] :
        if(not tech_key in parents):
            #Lets start down this tree
            process_node(0,doctrine,tech_key,[tech_key],{})

print(json.dumps(output["land_doctrine_folder"][4],indent=2,sort_keys=True))