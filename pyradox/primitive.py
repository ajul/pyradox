import collections
import re

class ParseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def makeBool(tokenString):
    """
    Converts a token string to a boolean.
    """
    return tokenString in ('yes', 'true')

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

daysPerMonth0 = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

DateBase = collections.namedtuple('DateBase', ['year', 'month', 'day'])
DurationBase = collections.namedtuple('DurationBase', ['years', 'months', 'days'])

def dateArgs(args):
    if len(args) == 1:
        if isinstance(args[0], str):
            args = args[0].split('.')
        else:
            args = args[0]

    args = [int(x) for x in args]
    return args

def clampDayArgs(args):
    year, month, day = dateArgs(args)
    if day > daysPerMonth0[month - 1]: day = daysPerMonth0[month - 1]
    elif day < 1: day = 1
    return year, month, day

class Date(DateBase):
    """
    Represents a date. Can be defined using e.g.:
    Date('1444.1.1')
    Date(year=1444, month=1, day=1)
    """
    def __new__(cls, *args, **kwargs):
        return DateBase.__new__(cls, *clampDayArgs(args), **kwargs)
    
    def __repr__(self):
        return '%d.%d.%d' % (self.year, self.month, self.day)
        
    def __int__(self):
        # number of days since 0.0.0
        yearDays = 365 * self.year
        monthDays = sum(daysPerMonth0[:self.month])
        return yearDays + monthDays + self.day

    def __add__(self, other):
        """add a Duration to this date"""
        if isinstance(other, Duration):
            totalMonths = (self.year + other.years) * 12 + (self.month - 1) + other.months
            day0 = (self.day - 1) + other.days

            # add full years from days
            totalMonths += (day0 // 365) * 12
            day0 = day0 % 365

            # add remaining days
            while day0 >= daysPerMonth0[totalMonths % 12]:
                day0 -= daysPerMonth0[totalMonths % 12]
                totalMonths += 1

            # compute years and months
            year = totalMonths // 12 
            month0 = totalMonths % 12
            
            return Date(year, month0 + 1, day0 + 1)
        else:
            raise TypeError('Only a Duration may be added to a Date.')
            
    def __sub__(self, other):
        """ Subtract a Date from a Date -> int or a Duration from a Date -> Date  """
        if isinstance(other, Date):
            return int(self) - int(other)
        elif isinstance(other, Duration):
            #TODO
            raise NotImplementedError()
        else:
            raise TypeError('Only a Duration may be added to a Date.')

    def yearsAfter(self, other):
        """the number of year boundaries between this and the other date"""
        return self.year - other.year

    def monthsAfter(self, other):
        """the number of month boundaries between this and the other date"""
        return (self.year - other.year) * 12 - (self.month - other.month)

    def daysAfter(self, other):
        #TODO
        raise NotImplementedError()

class Duration(DurationBase):
    """
    Represents a timespan. Can be defined using e.g.:
    Date(months=12)
    """
    def __new__(cls, *args, **kwargs):
        # defaults
        if not args:
            if 'years' not in kwargs: kwargs['years'] = 0
            if 'months' not in kwargs: kwargs['months'] = 0
            if 'days' not in kwargs: kwargs['days'] = 0
        return DurationBase.__new__(cls, *dateArgs(args), **kwargs)

tokenPatterns = [
    ('date', r'\d{,4}\.\d{,2}\.\d{,2}\b'),
    ('float', r'-?(\d+\.\d*|\d*\.\d+)\b'),
    ('int', r'-?\d+\b'),
    ('bool', r'(yes|no)\b'),
    ('str', r'".*?["\n]|[^#=\{\}\s]+'), # allow strings to end with newline instead of "; do escape characters exist?
]

keyConstructors = {
    'date' : Date,
    'int' : int,
    'str' : str,
    }

constructors = {
    'date' : Date,
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

# unit test
if __name__ == "__main__":
    print(Date('1444.12.14') + Duration(days=20))
