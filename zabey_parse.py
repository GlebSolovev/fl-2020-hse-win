#!/usr/bin/env python3

import ply.yacc as yacc
import sys

from lex import tokens

# S -> M R+ | R+ | M
# M -> 'MODULE' I 'DOT'
# R -> A 'ASSIGN' D 'DOT' | A 'DOT'

# D -> C 'DISJ' D | C
# C -> E 'CONJ' C | E
# E -> A | 'LBR' D 'RBR'

# A -> 'ID' Z | 'ID'
# Z -> W Z | W
# W -> I | 'LBR' I Z 'RBR'| 'LBR' W 'RBR'

# I -> 'MODULE' | 'ID'


def closeInBrackets(s):
    if (s.startswith('(') and s.endswith(')')):
        return s
    if (' ' not in s):
        return s
    return "(" + s + ")"


def p_prog(p):  # P -> R+ | M R+
    '''prog : relations
            | module relations'''
    if len(p) > 2:
        p[0] = p[1] + "\n" + p[2]
    else:
        p[0] = p[1]


def p_prog_norelations(p):  # P -> M
    'prog : module'
    p[0] = p[1]


def p_module(p):  # M -> 'MODULE' I 'DOT'
    'module : MODULE id DOT'
    p[0] = "Module " + p[2]


def p_relations_sequence(p):  # S -> R S
    'relations : relation relations'
    p[0] = p[1] + "\n" + p[2]


def p_relations_relation(p):  # S -> R
    'relations : relation'
    p[0] = p[1]


def p_relation_assign(p):  # R -> A 'ASSIGN' D 'DOT'
    'relation : atom ASSIGN disjexpr DOT'
    p[0] = "Assign " + closeInBrackets(p[1]) + " " + closeInBrackets(p[3])


def p_relation_atom(p):  # R -> A 'DOT'
    'relation : atom DOT'
    p[0] = p[1]


def p_disjexpr_disjunction(p):  # D -> C 'DISJ' D
    'disjexpr : conjexpr DISJ disjexpr'
    p[0] = "Disjunction " + closeInBrackets(p[1]) + " " + closeInBrackets(p[3])


def p_disjexpr_conjexpr(p):  # D -> C
    'disjexpr : conjexpr'
    p[0] = p[1]


def p_conjexpr_conjunction(p):  # C -> E 'CONJ' C
    'conjexpr : elemexpr CONJ conjexpr'
    p[0] = "Conjunction " + closeInBrackets(p[1]) + " " + closeInBrackets(p[3])


def p_conjexpr_elemexpr(p):  # C -> E
    'conjexpr : elemexpr'
    p[0] = p[1]


def p_elemexpr_id(p):  # E -> A
    'elemexpr : atom'
    p[0] = p[1]


def p_elemexpr_brackets(p):  # E -> 'LBR' D 'RBR'
    'elemexpr : LBR disjexpr RBR'
    p[0] = closeInBrackets(p[2])


def p_atom_sequence(p):  # A -> I Z
    'atom : id atomseq'
    p[0] = p[1] + " " + p[2]


def p_atom_id(p):  # A -> I
    'atom : id'
    p[0] = p[1]


def p_atomseq_seq(p):  # Z -> W Z
    'atomseq : elematom atomseq'
    p[0] = p[1] + " " + p[2]


def p_atomseq_elematom(p):  # Z -> W
    'atomseq : elematom'
    p[0] = p[1]


def p_elematom_id(p):  # W -> I
    'elematom : id'
    p[0] = p[1]


def p_elematom_atombrackets(p):  # W -> 'LBR' I Z 'RBR'
    'elematom : LBR id atomseq RBR'
    p[0] = closeInBrackets(p[2] + " " + p[3])


def p_elematom_elematombrackets(p):  # W -> 'LBR' W 'RBR'
    'elematom : LBR elematom RBR'
    p[0] = closeInBrackets(p[2])


def p_id_module(p):  # I -> 'MODULE'
    'id : MODULE'
    p[0] = p[1]


def p_id_id(p):  # I -> 'ID'
    'id : ID'
    p[0] = p[1]


def p_error(p):
    global err_logs
    if not p:
        err_logs += "Syntax error: next token is expected, but eof reached\n"
        return
    err_logs += "Syntax error at token " + str(
        [p.type, p.value, p.lineno, p.lexpos]) + ", skip to the next 'DOT'\n"
    while True:
        tok = parser.token()
        if not tok or tok.type == 'DOT':
            break
    parser.restart()


err_logs = ""
parser = yacc.yacc()


def parseFile(filename):
    with open(filename, "r") as finp:
        result = parser.parse(finp.read())
    if not result: result = "End of input reached while skipping or parsing"
    return err_logs + result


def writeToFile(filename, s):
    #print(s)
    with open(filename, "w") as fout:
        print(s, file=fout)


if len(sys.argv) >= 2:
    filename = sys.argv[1]
    writeToFile(filename + ".out", parseFile(filename))
