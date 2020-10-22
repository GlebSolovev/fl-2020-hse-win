#!/usr/bin/env python3

import sys
from parse import parser


def test_failed(message, s, ans, result):
    print("Test failed: " + message)
    print("input: " + s)
    print("correct answer: " + ans)
    print("parse.py answer: " + result)
    sys.exit(1)


def test_parse(s, ans):
    result = parser.parse(s)
    if not ans:
        if not result: return
        test_failed("parsed relation instead of syntax error", s, "None",
                    result)
    if not result:
        test_failed("syntax error instead of accept", s, ans, "None")
    elif result != ans:
        test_failed("wrong AST", s, ans, result)


def test_accept():
    accept_relations = [
        ["f.", "f"], ["f :- g.", "Assign f g"],
        ["f :- g, h; t.", "Assign f (Disjunction (Conjunction g h) t)"],
        ["f :- g, (h; t).", "Assign f (Conjunction g (Disjunction h t))"],
        ["f :- ((g), h).", "Assign f (Conjunction g h)"],
        ["f :- ((g); h).", "Assign f (Disjunction g h)"],
        ["f a :- g, h (t c d).", "Assign (f a) (Conjunction g (h (t c d)))"],
        [
            "f (cons h t) :- g, h, f t.",
            "Assign (f (cons h t)) (Conjunction g (Conjunction h (f t)))"
        ], ["f (((g))).", "f g"], ["f g.", "f g"], ["f g h.", "f g h"],
        ["f :- a, (a (a b) t).", "Assign f (Conjunction a (a (a b) t))"],
        [
            "f (g (h t)) :- ((f; g), (r), (h, t (g h) g)), a; b; c.",
            "Assign (f (g (h t))) (Disjunction (Conjunction (Conjunction (Disjunction f g) (Conjunction r (Conjunction h (t (g h) g)))) a) (Disjunction b c))"
        ]
    ]
    for [rel, ans] in accept_relations:
        test_parse(rel, ans)
    print("test accept relations: OK")

    accept_progs = [[
        "module m.\nf :- module, h.\ng module :- aaw.",
        "Module m\nAssign f (Conjunction module h)\nAssign (g module) aaw"
    ], ["f :- g.", "Assign f g"],
                    [
                        "module module. module :- module.",
                        "Module module\nAssign module module"
                    ],
                    [
                        "module module. module module.",
                        "Module module\nmodule module"
                    ], ["module module.", "Module module"],
                    ["module module module.", "module module module"],
                    ["module.", "module"]]
    for [prog, ans] in accept_progs:
        test_parse(prog, ans)
    test_parse("".join([rel for [rel, ans] in accept_relations]),
               "\n".join([ans for [rel, ans] in accept_relations]))
    print("test accept programm: OK")


def test_syntax_error():
    syntax_error_relations = [
        "f", ":- f.", "f :- .", "f :- g; h, .", "f :- ((g h) (t h)), g.",
        "f (((h) t) (g)).", "f :- (g; (f).", "f ().", "f :- ().", "(f).",
        "(f) :- g.", "(f g h) :- g.", "(f :-) g.", "(f ((t) (g h))).",
        "f :- (g, (h;) t)."
    ]
    for rel in syntax_error_relations:
        test_parse(rel, None)
    print("test syntax-error relations: OK")


test_accept()
test_syntax_error()
