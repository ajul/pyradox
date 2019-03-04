import pyradox
import pyradox.config
import pyradox.token
from pyradox.error import *

import re
import os
import warnings

game_encodings = {
    'EU4' : ['cp1252', 'utf_8_sig'],
    'HoI3' : ['cp1252', 'utf_8_sig'],
    'HoI3_vanilla' : ['cp1252', 'utf_8_sig'],
    'HoI4' : ['utf_8_sig', 'cp1252'],
    'HoI4_beta' : ['utf_8_sig', 'cp1252'],
    'Stellaris' : ['utf_8_sig', 'cp1252'],
}
        
def readlines(filename, encodings):
    for encoding in encodings:
        try:
            with open(filename, encoding=encoding) as f:
                lines = f.readlines()
            return lines
        except UnicodeDecodeError:
            warnings.warn(ParseWarning("Failed to decode input file %s using codec %s." % (filename, encoding)))
    raise ParseError("All codecs failed for input file %s." % filename)

def parse(s, filename="<string>"):
    """Parse a string."""
    lines = s.splitlines()
    token_data = lex(lines, filename)
    return parse_tree(token_data, filename)

def should_parse(fullpath, filename, filter_pattern = None):
    if not os.path.isfile(fullpath): return False
    _, ext = os.path.splitext(fullpath)
    if not ext == '.txt': return False
    if filter_pattern is not None and not re.search(filter_pattern, filename): return False
    return True

def parse_file(path, game=None, path_relative_to_game=True, verbose=False):
    """
    Parse a single file and return a Tree.
    path, game: 
        If game is None, path is a full path and the game is determined from that.
        Or game can be supplied, in which case path is a path relative to the game directory.
    """
    if not path_relative_to_game:
        pass
    else:
        path, game = pyradox.config.combine_path_and_game(path, game)
    encodings = game_encodings[game]
    
    lines = readlines(path, encodings)
    if verbose: print('Parsing file %s.' % path)
    token_data = lex(lines, path)
    return parse_tree(token_data, path)
    
def parse_dir(path, game=None, filter_pattern = None, *args, **kwargs):
    """Given a directory, iterate over the content of the .txt files in that directory as Trees"""
    path, game = pyradox.config.combine_path_and_game(path, game)
    
    for filename in os.listdir(path):
        fullpath = os.path.join(path, filename)
        if should_parse(fullpath, filename, filter_pattern):
            yield filename, parse_file(fullpath, game = game, *args, **kwargs)

def parse_merge(path, game=None, filter_pattern = None, merge_levels = 0, apply_defines = False, *args, **kwargs):
    """Given a directory, return a Tree as if all .txt files in the directory were a single file"""
    path, game = pyradox.config.combine_path_and_game(path, game)
    
    result = pyradox.Tree()
    for filename in os.listdir(path):
        fullpath = os.path.join(path, filename)
        if os.path.isfile(fullpath):
            if should_parse(fullpath, filename, filter_pattern):
                tree = parse_file(fullpath, game = game, *args, **kwargs)
                if apply_defines:
                    tree = tree.apply_defines()
                result.merge(tree, merge_levels)
    return result

def parse_walk(dirname, filter_pattern = None, *args, **kwargs):
    """Given a directory, recursively iterate over the content of the .txt files in that directory as Trees"""
    for root, dirs, files in os.walk(dirname):
        for filename in files:
            fullpath = os.path.join(root, filename)
            if should_parse(fullpath, filename, filter_pattern):
                yield filename, parse_file(fullpath, *args, **kwargs)

# open questions:
# what characters are allowed in key strings?
# in value strings?
# are there escape characters?

token_types = [
    # keysymbols
    ('whitespace', r'\s+'),
    ('operator', r'<=?|>=?|='),
    ('begin', r'\{'),
    ('end', r'\}'),
    ('comment', r'#.*'),
    ] + pyradox.token.token_patterns

omnibus_pattern = ''
for token_type, p in token_types:
    omnibus_pattern += '(?P<' + token_type + '>' + p + ')'
    omnibus_pattern += '|'
omnibus_pattern += '(.+)'

omnibus_pattern = re.compile(omnibus_pattern)

def lex(file_lines, filename):
    return list(lex_iter(file_lines, filename))

def lex_iter(file_lines, filename):
    """Lexer. Given the contents of a file, produces a list of (token_type, token_string, line_number)."""
    return (
        (m.lastgroup, m.group(0), line_number)
        for line_number, line in enumerate(file_lines)
        for m in omnibus_pattern.finditer(line) if m.lastgroup not in ('whitespace',)
        )
        
class TreeParseState():
    def __init__(self, token_data, filename, start_pos, is_top_level):
        self.token_data = token_data          # The tokenized version of the file. List of (token_type, token_string, token_line_number) tuples.
        self.filename = filename            # File the tree is being parsed from. Used for warning and error messages.
        self.is_top_level = is_top_level        # True iff this tree is the top level of the file.
    
        self.result = pyradox.Tree() # The resulting tree.
        
        self.pos = start_pos                 # Current token position.
        self.pending_comments = []           # Comments pending assignment.
        self.key = None                     # The key currently being processed.
        self.key_string = None               # The original token string for that key.
        self.operator = None                # The operator currently being processed. Usually '='.
        self.in_group = False               # Whether the parser is currently inside a group.
        self.next = self.process_key         # The next case to execute.
    
    def get_previous_line_number(self):
        """ Line number of the token just before the one consumed. Returns -1 if the token just consumed was the first one."""
        if len(self.token_data) > 0 and self.pos > 1:
            return self.token_data[self.pos-2][2]
        return -1
    
    def parse(self):
        """ Called once to parse. """
        while self.pos < len(self.token_data) and self.next is not None:
            self.next() # Keep parsing.
        
        # End of tree reached.
        if self.next is None:
            self.result.end_comments = self.pending_comments
            return self.result, self.pos
        
        # End of file reached.
        if self.is_top_level:
            self.result.end_comments = self.pending_comments
            return self.result
        else:
            warnings.warn_explicit('Cannot end inner level with end of file.', ParseWarning, self.filename, self.get_previous_line_number() + 1)
            return self.result, self.pos
    
    def consume(self):
        """ Read the next tuple from the list and advance the position counter. """
        token_type, token_string, token_line_number = self.token_data[self.pos]
        self.pos += 1
        return token_type, token_string, token_line_number
        
    def append_to_result(self, value):
        """ 
        Append the current value to result. 
        key, operator, and other arguments are set by internal state.
        Also consumes any pending comments.
        """
        self.result.append(self.key, value, pre_comments = self.pending_comments, operator = self.operator, in_group = self.in_group)
        self.pending_comments = []
        
    def append_line_comment(self, comment):
        """
        Appends a line comment if not already set; otherwise appends to post_comments.
        """
        
        if len(self.result) == 0: return
        
        if self.result.get_line_comment_at(-1) is None:
            self.result.set_line_comment_at(-1, comment)
        else:
            self.result.get_post_comments_at(-1).append(comment)
        
    def process_key(self):
        token_type, token_string, token_line_number = self.consume()
        
        if pyradox.token.is_primitive_key_token_type(token_type):
            self.key_string = token_string
            self.key = pyradox.token.make_primitive(token_string, token_type)
            self.next = self.process_operator
        elif token_type == 'comment':
            if token_line_number == self.get_previous_line_number():
                # Comment following a previous value.
                self.append_line_comment(token_string[1:])
            else:
                self.pending_comments.append(token_string[1:])
            self.next = self.process_key
        elif token_type == 'end':
            if self.is_top_level:
                # top level cannot be ended, warn
                warnings.warn_explicit('Unmatched closing bracket at outer level of file. Skipping token.', ParseWarning, self.filename, token_line_number + 1)
                self.next = self.process_key
            else:
                self.next = None
        else:
            #invalid key
            warnings.warn_explicit('Token "%s" is not valid key. Skipping token.' % token_string, ParseWarning, self.filename, token_line_number + 1)
            self.next = self.process_key
    
    def process_operator(self):
        # expecting an operator
        token_type, token_string, token_line_number = self.consume()
        
        if token_type == 'operator':
            self.operator = token_string
            self.next = self.process_value
        elif token_type == 'comment':
            self.pending_comments.append(token_string[1:])
            self.next = self.process_operator
        else:
            # missing operator; unconsume the token and move on
            warnings.warn_explicit('Expected operator after key "%s". Treating operator as "=" and token "%s" as value.' % (self.key_string, token_string), ParseWarning, self.filename, token_line_number + 1)
            self.pos -= 1
            self.operator = '='
            self.next = self.process_value
        
    def process_value(self):
        # expecting a value
        token_type, token_string, token_line_number = self.consume()
        
        if pyradox.token.is_primitive_value_token_type(token_type):
            maybe_color = self.maybe_subprocess_color(token_string, token_line_number)
            if maybe_color is not None:
                value = maybe_color
            else:
                # normal value
                value = pyradox.token.make_primitive(token_string, token_type)
            self.append_to_result(value)
            
            if self.in_group:
                self.next = self.process_value
            else:
                self.next = self.process_key
        elif token_type == 'begin':
            # Value is a tree or group. First, determine whether this is a tree or group.
            lookahead_pos = self.pos
            level = 0
            
            # Empty brackets are trees by default.
            is_tree = True
            while lookahead_pos < len(self.token_data) and level >= 0:
                token_type, token_string, token_line_number = self.token_data[lookahead_pos]
                lookahead_pos += 1
                
                if level == 0:
                    if token_type == 'operator':
                        # If an operator is found at this level, it's definitely a tree.
                        is_tree = True
                        break
                    elif token_type not in ['comment', 'end']:
                        # If something else (other than a comment or end) is found at this level, 
                        # then it's a group unless an operator is found later.
                        is_tree = False
                
                if token_type == 'begin':
                    level += 1
                elif token_type == 'end':
                    level -= 1

            if is_tree:
                # Recurse.
                value, self.pos = parse_tree(self.token_data, self.filename, self.pos)
                self.append_to_result(value)
                
                if self.in_group:
                    self.next = self.process_value
                else:
                    self.next = self.process_key
            else:
                # Process following values as a group.
                if self.in_group:
                    raise ParseError('%s, line %d: Error: Cannot nest groups inside groups.' % (self.filename, token_line_number + 1))
                else:
                    self.in_group = True
                    self.next = self.process_value
        elif token_type == 'comment':
            if self.in_group:
                if token_line_number == self.get_previous_line_number():
                    self.append_line_comment(token_string[1:])
                else:
                    self.pending_comments.append(token_string[1:])
            else:
                self.pending_comments.append(token_string[1:])
            self.next = self.process_value
        elif token_type == 'end' and self.in_group:
            self.in_group = False
            self.next = self.process_key
        else:
            raise ParseError('%s, line %d: Error: Invalid token type %s after key "%s", expected a value type.' % (self.filename, token_line_number + 1, token_type, self.key_string))
        
    def maybe_subprocess_color(self, colorspace_token_string, colorspace_token_line_number):
        # Try to parse a color. 
        # Return the color if this is a color and change the parser state to match. 
        # Otherwise, return None with no change in parser state.
        colorspace = colorspace_token_string.lower()
        
        if colorspace not in pyradox.Color.COLORSPACES:
            return None
        
        # Possible comments to add.
        maybe_pre_comments = []
        
        # Expected sequence of non-comment tokens.
        COLOR_SEQUENCE = [['begin']] + [['int', 'float']] * 3 + [['end']]
        
        # Current position in the sequence.
        seq = 0
        
        channels = []
        
        maybe_pos = self.pos
        
        while maybe_pos < len(self.token_data):
            token_type, token_string, token_line_number = self.token_data[maybe_pos]
            maybe_pos += 1
            if token_type == 'comment':
                maybe_pre_comments.append(token_string)
            elif token_type in COLOR_SEQUENCE[seq]:
                if token_type in ['int', 'float']:
                    channels.append(pyradox.token.make_primitive(token_string, token_type))
                seq += 1
                if seq >= len(COLOR_SEQUENCE):
                    # Finished color. Update state.
                    self.pending_comments += maybe_pre_comments
                    self.pos = maybe_pos
                    color = pyradox.Color(channels, colorspace)
                    return color
            else:
                # Unexpected token.
                break
        
        warnings.warn_explicit('Found colorspace token %s without following color.' % (colorspace_token_string.lower()), ParseWarning, self.filename, colorspace_token_line_number + 1)
        return None

def parse_tree(token_data, filename, start_pos = 0):
    """Given a list of (token_type, token_string, line_number) from the lexer, produces a Tree."""
    is_top_level = (start_pos == 0)
     # if starting position is 0, check for extra token at beginning
    if start_pos == 0 and len(token_data) >= 1 and re.search('txt$', token_data[0][1]):
        token_type, token_string, line_number = token_data[0]
        print('%s, line %d: Skipping header token "%s".' % (filename, line_number + 1, token_string))
        start_pos = 1 # skip first token
    
    state = TreeParseState(token_data, filename, start_pos, is_top_level)
    return state.parse()
