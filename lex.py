#!/usr/bin/env python3

import ply.lex as lex
import sys

# LEXER #
reserved = {'module': 'MODULE'}

tokens = ['ASSIGN', 'CONJ', 'DISJ', 'DOT', 'LBR', 'RBR', 'ID'] + list(
    reserved.values())

t_ASSIGN = r':-'
t_CONJ = r'\,'
t_DISJ = r'\;'
t_DOT = r'\.'
t_LBR = r'\('
t_RBR = r'\)'


def t_ID(t):  # add starts with lowercase, not var
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0] + ", exiting")
    #t.lexer.skip(1)
    sys.exit(1)


lexer = lex.lex()
