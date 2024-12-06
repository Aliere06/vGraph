import tabulate
import os
from ply import yacc
from vGraph_lexxer import tokens
from vGraph_lexxer import lexer

errors = 0

#== GRAMMAR RULES ==
#=PROGRAM STRUCTURE
def p_program(p):
    'program : lines'
    p[0] = p[1]

def p_lines(p):
    'lines : lines LINE_BREAK line'
    p[0] = f'{p[1]}{p[2]}{p[3]}'

def p_lines_line(p):
    'lines : line'
    p[0] = p[1]
    
def p_line(p):
    '''line : type_expression
        | assignment_expression
        | arithmetic_expression
        | graph_expression
        | function_call'''
    p[0] = p[1]
    
#=MISC
def p_plain_values(p):
    '''plain_value : INTEGER
        | DECIMAL
        | STRING
        | node
        | graph'''
    p[0] = p[1]

def p_error(p):
    global errors
    errors += 1

#=EXPRESSIONS
#Type expressions
def p_type_ex(p):
    '''type_expression : TYPE ID
        | L_BRACKET TYPE R_BRACKET ID'''
    if len(p) == 3:
        p[0] = f'{p[1]} {p[2]}'
    else:
        p[0] = f'{p[1]}{p[2]}{p[3]} {p[4]}'

#Assignment expressions
def p_assignment_ex(p):
    '''assignment_expression : type_expression ASSIGN_OP assignable
        | ID ASSIGN_OP assignable
        | assignable ASSIGN_OP type_expression
        | assignable ASSIGN_OP ID'''
    p[0] = f'{p[1]} {p[2]} {p[3]}'

def p_assignable(p):
    '''assignable : ID
        | plain_value
        | arithmetic_expression
        | graph_expression'''
    p[0] = p[1]

#Arithmetic expressions
def p_arithmetic_ex(p):
    '''arithmetic_expression : ari_operand ari_operator arithmetic_expression
        | ari_operand'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f'{p[1]} {p[2]} {p[3]}'

def p_ari_operand(p):
    '''ari_operand : INTEGER
        | DECIMAL
        | ID'''
    p[0] = p[1]

def p_ari_operator(p):
    '''ari_operator : PLUS_OP
        | MINUS_OP
        | TIMES_OP
        | OVER_OP'''
    p[0] = p[1]

#Graph expressions
def p_graph_expression(p):
    '''graph_expression : graph_operand graph_operator graph_expression
        | graph_operand'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f'{p[1]} {p[2]} {p[3]}'

def p_graph_operand(p):
    '''graph_operand : node
        | ID'''
    p[0] = p[1]

def p_graph_operator(p):
    '''graph_operator : CONNECT_OP
        | DISCONNECT_OP
        | L_CONNECT_OP
        | R_CONNECT_OP
        | WEIGHT_OP
        | L_WEIGHT_OP
        | R_WEIGHT_OP'''
    p[0] = p[1]

def p_node(p):
    '''node : plain_node
        | plain_node node_connections
        | ID'''
    if len(p) == 3:
        p[0] = f'{p[1]}{p[2]}'
    else:
        p[0] = p[1]

def p_plain_node(p):
    '''plain_node : N_PARENTHESIS plain_value R_PARENTHESIS
        | N_PARENTHESIS R_PARENTHESIS'''
    if len(p) == 3:
        p[0] = f'{p[1]}{p[2]}'
    else:
        p[0] = f'{p[1]}{p[2]}{p[3]}'

def p_node_connections(p):
    '''node_connections : L_PARENTHESIS node_list R_PARENTHESIS
        | L_PARENTHESIS R_PARENTHESIS'''
    if len(p) == 3:
        p[0] = f'{p[1]}{p[2]}'
    else:
        p[0] = f'{p[1]}{p[2]}{p[3]}'

def p_node_list(p):
    '''node_list : node_list COMMA node
        | node'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f'{p[1]}{p[2]} {p[3]}'

def p_graph(p):
    '''graph : G_BRACKET node_list R_BRACKET
        | G_BRACKET R_BRACKET
        | ID'''
    if len(p) == 3:
        p[0] = f'{p[1]}{p[2]}'
    elif len(p) == 2:
        p[0] =p[1]
    else: 
        p[0] = f'{p[1]}{p[2]}{p[3]}'
        
#=FUNCTION CALLS
def p_function_call(p):
    '''function_call : add
        | remove
        | join
        | subtract
        | intersect
        | reverse
        | disconnect
        | connect_all
        | path_find'''
    p[0] = p[1]

def p_add(p):
    '''add : ADD_FUNC L_PARENTHESIS graph COMMA node_list R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]} {p[5]}{p[6]}'

def p_remove(p):
    '''remove : REMOVE_FUNC L_PARENTHESIS graph COMMA node_list R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]} {p[5]}{p[6]}'

def p_join(p):
    '''join : JOIN_FUNC L_PARENTHESIS graph COMMA graph R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]} {p[5]}{p[6]}'

def p_subtract(p):
    '''subtract : SUBTRACT_FUNC L_PARENTHESIS graph COMMA graph R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]} {p[5]}{p[6]}'

def p_intersect(p):
    '''intersect : INTERSECT_FUNC L_PARENTHESIS graph COMMA graph R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]} {p[5]}{p[6]}'

def p_reverse(p):
    '''reverse : REVERSE_FUNC L_PARENTHESIS graph R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]}'

def p_disconnect(p):
    '''disconnect : DISCONNECT_FUNC L_PARENTHESIS graph R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]}'

def p_connect_all(p):
    '''connect_all : CONNECT_ALL_FUNC L_PARENTHESIS graph R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]}'

def p_path_find(p):
    '''path_find : PATH_FIND_FUNC L_PARENTHESIS node COMMA node R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]} {p[5]}{p[6]}'

def p_degree(p):
    '''degree : DEGREE_FUNC L_PARENTHESIS node R_PARENTHESIS'''
    p[0] = f'{p[1]}{p[2]}{p[3]}{p[4]}'
    

# Build the parser
parser: yacc = yacc.yacc(debug=True)

while True:
    os.system('cls')
    errors = 0
    print("=== Graph Theory Language ===")
    print("1. Enter expression")
    print("2. Read file")
    selection = input()
    
    if selection == "1":
        print("Write the expression: ")
        expression = input()
        parser.parse(expression)
        result = "Valid expression" if errors == 0 else "Invalid expression"
        lexer.input(expression)
        token_data = []
        while True:
            tok = lexer.token()
            if not tok:
                break      # No more input
            token_data.append({"Type": tok.type, "Value":tok.value})

        print(tabulate.tabulate(token_data, headers="keys", tablefmt="grid"))
        print(result)
    elif selection == "2":
        print("Enter a file name: ")
        file_name = input()
        try:
            file_text = open(file_name, encoding="UTF-8").read()
            parser.parse(file_text)
            #print("parsing")
            result = "Valid expression" if errors == 0 else "Invalid expression"
            lexer.input(file_text)
            token_data = []
            while True:
                tok = lexer.token()
                if not tok:
                    break      # No more input
                token_data.append({"Type": tok.type, "Value":tok.value})

            print(file_text)
            print(tabulate.tabulate(token_data, headers="keys", tablefmt="grid"))
            print(result)
        except:
            print("Error while reading file")
    else:
        print("Invalid option!")
    input("Enter to continue...")