#!/usr/bin/env python3

import ply.lex as lex
import sys

# LEXER #
tokens = ['ASSIGN', 'CONJ', 'DISJ', 'DOT', 'LBRACKET', 'RBRACKET', 'ID']

t_ASSIGN = r':-'
t_CONJ = r'\,'
t_DISJ = r'\;'
t_DOT = r'\.'
t_LBRACKET = r'\('
t_RBRACKET = r'\)'
t_ID = r'[a-zA-Z_][a-zA-Z_0-9]*'

t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

finp = open(sys.argv[1], "r")
lexer.input(finp.read())
finp.close()

tokens = []
while True:
    tok = lexer.token()
    if not tok:
        break
    tokens.append([tok.type, tok.value, tok.lineno, tok.lexpos])
tokens.append(["END", None])  # end of programm token

# PARSE WITH RECURSIVE DESCENT #
next_tok_index = -1
next_tok_t = None
nect_tok_v = None
level = 0

# grammar
# S -> M? R*
# M -> 'MODULE' 'ID' 'DOT'
# R -> H 'ASSIGN' D 'DOT' | H 'DOT'
# H -> 'ID'
# D -> C 'DISJ' D | C
# C -> E 'CONJ' C | E
# E -> 'ID' | 'LBRACKET' D 'RBRACKET'


def S():  # S -> M? R*
    enter('S')
    scan()
    if next_tok_t == 'END':
        sys.exit(1)
    M()  # if M fails, it won't change next_tok
    while True:
        R()
        if next_tok_t == 'END':
            sys.stdout.write(", accept.\n")
            sys.exit(1)
    leave('S')


def M():  # M -> 'module' 'ID' 'DOT'
    enter('M')
    if next_tok_v == 'module':
        scan()
        if next_tok_t == 'ID':
            scan()
            if next_tok_t == 'DOT':
                scan()
            else:
                # error("Expected dot at the end of module declaration")
                unscan()
        else:
            # error("Module name is not an ID")
            unscan()
    leave('M')


def R():  # R -> H 'ASSIGN' D 'DOT' | H 'DOT'
    enter('R')
    H()
    if next_tok_t == 'ASSIGN':
        scan()
        D()
    if next_tok_t == 'DOT':
        scan()
    else:
        error("Relation without dot")
    leave('R')


def H():  # H -> 'ID'
    enter('H')
    if next_tok_t == 'ID':
        scan()
    else:
        print(next_tok_t)
        error("Head is not an ID")
    leave('H')


def D():  # D -> C 'DISJ' D | C
    enter('D')
    C()
    if next_tok_t == 'DISJ':
        scan()
        D()
    leave('D')


def C():  # C -> E 'CONJ' C | E
    enter('C')
    E()
    if next_tok_t == 'CONJ':
        scan()
        C()
    leave('C')


def E():  # E -> 'ID' | 'LBRACKET' D 'RBRACKET'
    enter('E')
    if next_tok_t == 'ID':
        scan()
    elif next_tok_t == 'LBRACKET':
        scan()
        D()
        if next_tok_t == 'RBRACKET':
            scan()
        else:
            error("Missed RBRACKET")
    else:
        error("Elem-expr doesn't start with ID or LBRACKET")
    leave('E')


#class ParseFailed(Exception):
#    def __init__(self, message):
#        self.message = message
#
#    def __str__(self):
#        return message


def error(info):
    sys.stdout.write("\nError: " + str(info) + "\n")
    if 0 <= next_tok_index < len(tokens):
        sys.stdout.write("\nnext_tok was: " + str(tokens[next_tok_index]) +
                         "\n")
    sys.exit(1)


def scan():
    global next_tok_index, next_tok_t, next_tok_v
    next_tok_index += 1
    if next_tok_index >= len(tokens):
        error("Unexpected end of input text")
    next_tok_t = tokens[next_tok_index][0]
    next_tok_v = tokens[next_tok_index][1]


def unscan():
    global next_tok_index, next_tok_t, next_tok_v
    next_tok_index -= 1
    if next_tok_index < 0:
        error("Internal error: unscan made next_tok_index out of bounds")
    next_tok_t = tokens[next_tok_index][0]
    next_tok_v = tokens[next_tok_index][1]


def enter(name):
    global level
    spaces(level)
    level += 1
    sys.stdout.write("+-%c: Enter, \t" % name)
    sys.stdout.write("next_tok == " + str(tokens[next_tok_index]) + "\n")


def leave(name):
    global level
    level -= 1
    spaces(level)
    sys.stdout.write("+-%c: Leave, \t" % name)
    sys.stdout.write("next_tok == " + str(tokens[next_tok_index]) + "\n")


def spaces(local_level):
    while local_level > 0:
        local_level -= 1
        sys.stdout.write("| ")


# parse tokens
while True:
    S()
