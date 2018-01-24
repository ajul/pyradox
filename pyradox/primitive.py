import collections
import re
import warnings

from pyradox.error import ParseError, ParseWarning, ValueWarning

def make_bool(token_string):
    """
    Converts a token string to a boolean.
    """
    if token_string in ('yes', 'true'): return True
    elif token_string in ('no', 'false'): return False
    else: raise ValueError('Invalid token string %s for bool.' % token_string)

def make_string(token_string):
    """
    Converts a token string to a string by dequoting it.
    """
    return re.sub(r'^"(.*)"$', r'\1', token_string)

def make_token_string(value):
    """
    Converts a primitive value to a token string.
    """
    if isinstance(value, bool):
        if value: return 'yes'
        else: return 'no'
    elif isinstance(value, str):
        #quote string if contains non-alphanumerics or is empty
        if len(value) == 0 or re.search("\W", value):
            return '"%s"' % value
        else:
            return value
    else:
        return str(value)

HOURS_PER_DAY = 24
DAYS_PER_MONTH_0 = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] # No leap years.
DAYS_PER_YEAR = sum(DAYS_PER_MONTH_0)
TIME_PRECISIONS = ['year', 'month', 'day', 'hour']
MONTH_NAMES_0 = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

class Time():
    """
    Represents a time. Valid constructions:
    Provide a string, as in the .txt file, e.g. Time('1444.1.1')
    Explicitly named arguments: Time(year=1444, month=1, day=1)
    Ordered arguments: (1444, 1, 1)
    
    Presence or absence of hour is immutable after construction.
    """
    
    def __init__(self, year = None, month = None, day = None, hour = None):
        if isinstance(year, Time):
            # copy constructor
            self.data = [x for x in year.data]
        elif isinstance(year, str):
            # is actually string containing time data
            self.data = [int(x) for x in year.split('.')]
        else:
            self.data = [x for x in [year, month, day, hour] if x is not None]
        self.validate()
            
    def __lt__(self, other):
        return self.data < other.data
        
    def __le__(self, other):
        return self.data <= other.data
        
    def __gt__(self, other):
        return self.data > other.data
        
    def __ge__(self, other):
        return self.data >= other.data
        
    def __eq__(self, other):
        if not isinstance(other, Time): return False
        return self.data == other.data
        
    def __ne__(self, other):
        return not (self == other)
        
    def __iter__(self):
        for x in self.data: yield x
    
    def __getitem__(self, index):
        return self.data[index]
        
    def __setitem__(self, index, value):
        if index < len(self.data):
            self.data[index] = value
            self.validate(index)
        else:
            raise IndexError('Time lacks precision to %s.' % TIME_PRECISIONS[index])
        
    def __getattr__(self, name):
        if name in TIME_PRECISIONS:
            index = TIME_PRECISIONS.index(name)
            return self[index]
        else:
            raise AttributeError('Invalid time precision %s.' % name)
            
    def __setattr__(self, name, value):
        if name in TIME_PRECISIONS:
            index = TIME_PRECISIONS.index(name)
            self[index] = value
        else:
            super().__setattr__(name, value)
    
    def __str__(self):
        return '.'.join(str(x) for x in self.data)
    
    def human_name(self):
        result = ''
        if self.has_hour(): result += '%02d:00, ' % self.hour
        result += '%d %s %d' % (self.day, MONTH_NAMES_0[self.month-1], self.year)
        return result
    
    def has_hour(self):
        return len(self.data) >= 4
        
    def validate(self, index = None):
        if index is None:
            for index in range(len(TIME_PRECISIONS)):
                self.validate(index)
        elif index == 0:
            if self.year < 1: 
                warnings.warn(ValueWarning('Year is non-positive.'))
        elif index == 1:
            if self.month < 1 or self.month > 12: 
                raise ValueError('Month not in range 1-12.')
        elif index == 2:
            days_in_month = DAYS_PER_MONTH_0[self.month-1]
            if self.day < 1 or self.day > days_in_month: 
                warnings.warn(ValueWarning('Day not in range 1-%d for month %d.' % (days_in_month, self.month)))
        elif index == 3:
            if self.has_hour() and (self.hour < 1 or self.hour > 24): 
                warnings.warn(ValueWarning('Hour out of standard range 1-24.'))
    
    def days_since_1_ad(self):
        # number of days since 1.1.1
        year_days = DAYS_PER_YEAR * (self.year - 1)
        month_days = sum(days_per_month0[:(self.month-1)])
        return year_days + month_days + self.day - 1
        
    def hours_since_1_ad(self):
        return self.days_since_1_ad() * HOURS_PER_DAY + self.hours - 1
        
    @staticmethod
    def from_days_since_1_ad(days):
        year = days // DAYS_PER_YEAR + 1
        days = days % DAYS_PER_YEAR
        month = 1
        for days_in_month in DAYS_PER_MONTH_0:
            if days < days_in_month:
                day = days + 1
                break
            days -= days_in_month
            month += 1
        return Time(year, month, day)

    def years_after(self, other):
        """the number of year boundaries between this and the other time"""
        return self.year - other.year

    def months_after(self, other):
        """the number of month boundaries between this and the other time"""
        return self.years_after(other) * 12 + (self.month - other.month)

    def days_after(self, other):
        return days_since1ad(self) - days_since1ad(other)
        
    def hours_after(self, other):
        return self.days_after(other) + self.hours - other.hours

token_patterns = [
    ('time', r'\d+\.\d+\.\d+(\.\d+)?\b'),
    ('float', r'-?(\d+\.\d*|\d*\.\d+)\b'),
    ('int', r'-?\d+\b'),
    ('bool', r'(yes|no)\b'),
    ('str', r'"([^"\\\n]|\\.)*["\n]|[^#=\{\}\s]+'), # allow strings to end with newline instead of "; do escape characters exist?
]

key_constructors = {
    'time' : Time,
    'int' : int,
    'str' : str,
    }

constructors = {
    'time' : Time,
    'float' : float,
    'int' : int,
    'bool' : make_bool,
    'str' : make_string,
    }
    
def primitive_type_of(token_string):
    for token_type, pattern in token_patterns:
        m = re.match(pattern + '$', token_string)
        if m: return token_type
    return None
    
def is_primitive_key_token_type(token_type):
    return token_type in key_constructors.keys()
    
def is_primitive_value_token_type(token_type):
    return token_type in constructors.keys()

def make_primitive(token_string, token_type = None, default_token_type = None):
    if token_type is None:
        token_type = primitive_type_of(token_string)
        if token_type is None:
            if default_token_type is None:
                raise ParseError('Unrecognized token "%s". Should not occur.' % (token_string,))
            else:
                token_type = default_token_type
    return constructors[token_type](token_string)
