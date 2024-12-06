from ply import lex
import re
import tabulate

#TOKEN LISTS
reserved: list = [
    'FUNCTION',
    'IF',
    'ELSE',
    'RETURN',
]
punctuation: list = [
    'L_PARENTHESIS',    # (
    'R_PARENTHESIS',    # )
    'L_BRACKET',        # [
    'R_BRACKET',        # ]
    'COMMA',            # ,
    'G_BRACKET',        # g[
    'N_PARENTHESIS'     # n(
]
operators: list = [
    'PLUS_OP',              # +
    'MINUS_OP',             # -
    'TIMES_OP',             # *
    'OVER_OP',              # /
    'ASSIGN_OP',            # =
    'CONNECT_OP',           # ---
    'DISCONNECT_OP',        # -/-
    'L_CONNECT_OP',         # <--
    'R_CONNECT_OP',         # -->
    'WEIGHT_OP',    # -n-
    'L_WEIGHT_OP',  # <n-
    'R_WEIGHT_OP'   # -n>
]
types: dict = {
    'node':'NODE',
    'edge':'EDGE',
    'graph':'GRAPH',
    'int':'INTEGER', #\d+ --> 1234
    'dec':'DECIMAL',
    'str':'STRING',
}
language_functions: dict = {
    'add':'ADD_FUNC', #add --> add
    'remove':'REMOVE_FUNC',
    'join':'JOIN_FUNC',
    'subtract':'SUBTRACT_FUNC',
    'intersect':'INTERSECT_FUNC',
    'reverse':'REVERSE_FUNC',
    'disconnect':'DISCONNECT_FUNC',
    'connectAll':'CONNECT_ALL_FUNC',
    'pathFind':'PATH_FIND_FUNC',
    'degree':'DEGREE_FUNC'
}
misc: list = [
    'ID',
    'TYPE',
    'COMMENT',
    'LINE_BREAK'
]

tokens: list = (
    reserved + 
    punctuation + 
    operators + 
    list(types.values()) + 
    list(language_functions.values()) +
    misc
)

#== SIMPLE REGEX RULES ==
#Common expressions
integer_ex = r'''
[-\+]? #Optional sign
\d+ #Integer digits
'''
decimal_ex = r'''
[-\+]? #Optional sign
(?:\d+)? #Non-capturing, optional lhs digits
\. #Decimal point
\d+ #Rhs digits
'''
string_ex = r'''
\" #Start quotes
[^\"\n\r]* #Any chars except quotes and line breaks
\" #End quotes
'''
#Misc
t_ignore  = ' \t'
t_COMMENT = r'\/\/.*'
t_LINE_BREAK = r'\n|\r'
#Literals
t_L_PARENTHESIS = r'\('
t_R_PARENTHESIS = r'\)'
t_L_BRACKET     = r'\['
t_R_BRACKET     = r'\]'
t_COMMA         = r','
t_G_BRACKET     = r'g\['
t_N_PARENTHESIS = r'n\('
#Operators
t_PLUS_OP       = r'\+'
t_MINUS_OP      = r'-'
t_TIMES_OP      = r'\*'
t_OVER_OP       = r'\/'
t_ASSIGN_OP     = r'='
t_CONNECT_OP    = r'---'
t_DISCONNECT_OP = r'-\/-'
t_L_CONNECT_OP  = r'<--'
t_R_CONNECT_OP  = r'-->'

# t_WEIGHT_OP     = r'''
#     - #Connector start
#     (?P<WEIGHT> #Named capture group for weight value
#         ''' + integer_ex + r'''
#         | #Or
#         ''' + decimal_ex + r'''
#     )
#     - #Connector end
#     '''
# t_L_WEIGHT_OP   = r'<()-'
# t_R_WEIGHT_OP   = r'-()>'

#== REGEX RULES WITH ACTIONS ==
#Operators
def t_WEIGHT_OP(t):
    matches: re.Match = lexer.lexmatch
    start: str = matches.group("START")
    end: str = matches.group("END")
    
    if (start == "<") and (end == "-"):
        t.type = 'L_WEIGHT_OP'
    elif (start == "-") and (end == ">"):
        t.type = 'R_WEIGHT_OP'
    elif (start == "<") and (end == ">"):
        return t_error(t)
    
    weight: str = matches.group("WEIGHT")
    t.value = (t.value, float(weight) if weight.__contains__(".") else int(weight))
    return t
t_WEIGHT_OP.__doc__ = r'''
    (?P<START> -|<) #Connector start group
    (?P<WEIGHT> #Named capture group for weight value
        ''' + integer_ex + r'''
        | #Or
        ''' + decimal_ex + r'''
    )
    (?P<END> -|>) #Connector end group
'''
#Misc
def t_ID(t):
    value: str = str(t.value)
    if reserved.__contains__(value.upper()):
        t.type = value.upper()
    elif language_functions.__contains__(value):
        t.type = language_functions.get(value)
    elif types.__contains__(t.value):
        t.type = 'TYPE'
    return t
t_ID.__doc__ = r'''
    (?! #Negative lookahead, avoids matching:
        g\[ #Lone 'g' next to a bracket (G_BRACKET)
        | #Or 
        n\( #Lone 'n' next to a parenthesis (N_PARENTHESIS)
    )
    [a-zA-Z_]+ #1+ non digit chars
    [a-zA-Z_0-9]* #0+ id chars
'''
#Types
def t_DECIMAL(t):
    t.value = float(t.value)
    return t
t_DECIMAL.__doc__ = decimal_ex

def t_INTEGER(t):
    t.value = int(t.value)
    return t
t_INTEGER.__doc__ = integer_ex

def t_STRING(t):
    text: str = t.value
    t.value = (t.value, text.replace('"',''))
    return t
t_STRING.__doc__ = string_ex

"""
#New Line
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
"""

#Error handling
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

#== TESTS ==
lexer: lex.Lexer = lex.lex()
lexer.input(open("token test.txt").read())
token_data = []
'''
'''
while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    token_data.append({"Type": tok.type, "Value":tok.value})

print(tabulate.tabulate(token_data, headers="keys", tablefmt="grid"))