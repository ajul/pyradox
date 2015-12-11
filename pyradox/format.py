import re

def splitFilename(s):
    m = re.match(r'(\S*)\s*-?\s*(.*)\..*', s)
    return m.group(1), m.group(2)

def promoteTitle(s):
    def upperCase(m):
        return m.group(1) + m.group(2).upper()
    return re.sub(r'(^| )([a-z])', upperCase, s)
   
def capitalizeFirst(s):
    if s: return s[0].upper() + s[1:]
    else: return s

def humanString(s, capFirst = False):
    s = str(s)
    s = re.sub(r'\.txt', r'', s)
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
    s = re.sub(r'_', r' ', s)
    if capFirst: s = capitalizeFirst(s)
    # if len(s) == 3: s = s.upper()
    return s

def humanTitle(s):
    s = humanString(s)
    s = promoteTitle(s)
    return s    


