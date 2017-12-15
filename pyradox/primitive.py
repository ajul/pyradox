import collections
import re
import warnings

from pyradox.error import ParseError, ParseWarning, ValueWarning

def makeBool(tokenString):
    """
    Converts a token string to a boolean.
    """
    if tokenString in ('yes', 'true'): return True
    elif tokenString in ('no', 'false'): return False
    else: raise ValueError('Invalid token string %s for bool.' % tokenString)

def makeString(tokenString):
    """
    Converts a token string to a string by dequoting it.
    """
    return re.sub(r'^"(.*)"$', r'\1', tokenString)

def makeTokenString(value):
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
        if isinstance(year, str):
            # is actually string containing time data
            self.data = [int(x) for x in year.split('.')]
        else:
            self.data = [x for x in [year, month, day, hour] if x is not None]
        self.validate()
            
    def __lt__(self, other):
        return self.data < other.data
        
    def __eq__(self, other):
        return self.data == other.data
        
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
    
    def humanName(self):
        result = ''
        if self.hasHour(): result += '%02d:00, ' % self.hour
        result += '%d %s %d' % (self.day, MONTH_NAMES_0[self.month-1], self.year)
        return result
    
    def hasHour(self):
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
            daysInMonth = DAYS_PER_MONTH_0[self.month-1]
            if self.day < 1 or self.day > daysInMonth: 
                warnings.warn(ValueWarning('Day not in range 1-%d for month %d.' % (daysInMonth, self.month)))
        elif index == 3:
            if self.hasHour() and (self.hour < 1 or self.hour > 24): 
                warnings.warn(ValueWarning('Hour out of standard range 1-24.'))
    
    def daysSince1AD(self):
        # number of days since 1.1.1
        yearDays = DAYS_PER_YEAR * (self.year - 1)
        monthDays = sum(daysPerMonth0[:(self.month-1)])
        return yearDays + monthDays + self.day - 1
        
    def hoursSince1AD(self):
        return self.daysSince1AD() * HOURS_PER_DAY + self.hours - 1
        
    @staticmethod
    def fromDaysSince1AD(days):
        year = days // DAYS_PER_YEAR + 1
        days = days % DAYS_PER_YEAR
        month = 1
        for daysInMonth in DAYS_PER_MONTH_0:
            if days < daysInMonth:
                day = days + 1
                break
            days -= daysInMonth
            month += 1
        return Time(year, month, day)

    def yearsAfter(self, other):
        """the number of year boundaries between this and the other time"""
        return self.year - other.year

    def monthsAfter(self, other):
        """the number of month boundaries between this and the other time"""
        return self.yearsAfter(other) * 12 + (self.month - other.month)

    def daysAfter(self, other):
        return daysSince1AD(self) - daysSince1AD(other)
        
    def hoursAfter(self, other):
        return self.daysAfter(other) + self.hours - other.hours

tokenPatterns = [
    ('time', r'\d+\.\d+\.\d+(\.\d+)?\b'),
    ('float', r'-?(\d+\.\d*|\d*\.\d+)\b'),
    ('int', r'-?\d+\b'),
    ('bool', r'(yes|no)\b'),
    ('str', r'"([^"\\\n]|\\.)*["\n]|[^#=\{\}\s]+'), # allow strings to end with newline instead of "; do escape characters exist?
]

keyConstructors = {
    'time' : Time,
    'int' : int,
    'str' : str,
    }

constructors = {
    'time' : Time,
    'float' : float,
    'int' : int,
    'bool' : makeBool,
    'str' : makeString,
    }
    
def primitiveTypeOf(tokenString):
    for tokenType, pattern in tokenPatterns:
        m = re.match(pattern + '$', tokenString)
        if m: return tokenType
    return None
    
def isPrimitiveKeyTokenType(tokenType):
    return tokenType in keyConstructors.keys()
    
def isPrimitiveValueTokenType(tokenType):
    return tokenType in constructors.keys()

def makePrimitive(tokenString, tokenType = None, defaultTokenType = None):
    if tokenType is None:
        tokenType = primitiveTypeOf(tokenString)
        if tokenType is None:
            if defaultTokenType is None:
                raise ParseError('Unrecognized token "%s". Should not occur.' % (tokenString,))
            else:
                tokenType = defaultTokenType
    return constructors[tokenType](tokenString)
