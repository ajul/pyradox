import re

def split_filename(s):
    m = re.match(r'(\S*)\s*-?\s*(.*)\..*', s)
    return m.group(1), m.group(2)

def promote_title(s):
    def upper_case(m):
        return m.group(1) + m.group(2).upper()
    return re.sub(r'(^| )([a-z])', upper_case, s)
   
def capitalize_first(s):
    if s: return s[0].upper() + s[1:]
    else: return s

def human_string(s, cap_first = False):
    s = str(s)
    s = re.sub(r'\.txt', r'', s)
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
    s = re.sub(r'_', r' ', s)
    if cap_first: s = capitalize_first(s)
    # if len(s) == 3: s = s.upper()
    return s

def human_title(s):
    s = human_string(s)
    s = promote_title(s)
    return s    


