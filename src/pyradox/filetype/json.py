import json

def dump_tree(tree, fp, duplicate_action = 'list', **kwargs):
    """ 
    Dumps a Tree as json.dump.
    First converts to_python using duplicate_action.
    Additional kwargs are sent to json.dump.
    """
    obj = tree.to_python(duplicate_action = duplicate_action)
    json.dump(obj, fp, **kwargs)
    
def dumps_tree(tree, duplicate_action = 'list', **kwargs):
    """ 
    Dumps a Tree as json.dumps.
    First converts to_python using duplicate_action.
    Additional kwargs are sent to json.dumps.
    """
    obj = tree.to_python(duplicate_action = duplicate_action)
    return json.dumps(obj, **kwargs)