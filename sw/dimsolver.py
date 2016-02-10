# -*- coding: utf-8 -*-

import ply.lex as lex
import ply.yacc as yacc
import cmd

factors = {
    'nm': 1, 'um': 1e3, 'mm': 1e6, 'cm': 1e7, 'm' : 1e9,
    'in': 25.4e6, 'mil': 25.4e3, 'mils': 25.4e3
    }
system_unit = factors['nm']
default_unit = factors['mil']
optimize = False
debug = True

#      _
#     | |
#     | |     _____  _____ _ __
#     | |    / _ \ \/ / _ \ '__|
#     | |___|  __/>  <  __/ |
#     \_____/\___/_/\_\___|_|
#

tokens = ('NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'UNIT')

t_ignore = " \t"
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_UNIT    = r'mils?|mm|m|um|cm|in|nm'

def t_NUMBER(t):
    r'(?:\d+(?:[.,]\d+)?)|(?:[.,]\d+)'
    try:
        # TODO fazer aceitar virgula
        t.value = float(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex(optimize=optimize, debug=debug)

#     ______
#     | ___ \
#     | |_/ /_ _ _ __ ___  ___ _ __
#     |  __/ _` | '__/ __|/ _ \ '__|
#     | | | (_| | |  \__ \  __/ |
#     \_|  \__,_|_|  |___/\___|_|
#
precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

def p_statement_expr(t):
    'dim : value'
    t[0] = t[1]*default_unit/system_unit

def p_expression_binop(t):
    '''value : value PLUS value
             | value MINUS value
             | value TIMES value
             | value DIVIDE value'''
    if   t[2] == '+': t[0] = t[1] + t[3]
    elif t[2] == '-': t[0] = t[1] - t[3]
    elif t[2] == '*': t[0] = t[1] * t[3]
    elif t[2] == '/': t[0] = t[1] / t[3]

def p_expression_uminus(t):
    'value : MINUS value %prec UMINUS'
    t[0] = -t[2]

def p_expression_group(t):
    'value : LPAREN value RPAREN'
    t[0] = t[2]

def p_expression_unit(t):
    'value : NUMBER UNIT'
    t[0] = t[1]*factors.get(t[2], 1)/default_unit

def p_expression_number(t):
    'value : NUMBER'
    t[0] = t[1]

def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc(optimize=optimize, debug=debug)

#      _____         _
#     |_   _|       | |
#       | | ___  ___| |_ ___ _ __
#       | |/ _ \/ __| __/ _ \ '__|
#       | |  __/\__ \ ||  __/ |
#       \_/\___||___/\__\___|_|
#

class MeuTeste(cmd.Cmd):
    """MeuTeste """

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "mt> "
        self.intro  = "Executando o MeuTeste"

    def do_exit(self, args):
        return -1

    def do_EOF(self, args):
        return self.do_exit(args)

    def emptyline(self):
        pass

    def default(self, line):
        print '>>>> ', parser.parse(line, debug=debug)

if __name__ == '__main__':
    mt = MeuTeste()
    mt.cmdloop()
