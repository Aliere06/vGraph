import re

text: str = """
20
-1-
-+2-
--3-
-.4-
-+.5-
-++.5-
--+.5-
--.6-
-7.8-
-+8.9-
--9.0-
-+1.2.3-
"""

#exp1 = r'-([-\+]?\d+ | [-\+]?(?:\d+)?\.\d+)-'
exp2 = r'''
(?P<START> -|<) #Connector start
(?P<WEIGHT> #Capture group for weight value
    #Optionally signed integer
        [-\+]? #Optional sign
        \d+ #Integer digits
    | #Or
    #Optionally signed floating number
        [-\+]? #Optional sign
        (?:\d+)? #Non-capturing, optional lhs digits
        \. #Decimal point
        \d+ #Rhs digits
)
(?P<END> -|>) #Connector end
'''

print("matching")

matches = re.match(exp2, "<2.5>", re.VERBOSE)
print(matches.group("START"))