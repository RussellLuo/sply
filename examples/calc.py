#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sply.grammar import Grammar, token, production

# dictionary of names
names = {}


class Calc(Grammar):
    literals = '=+-*/()'

    precedences = [
        ('left', 'plus', 'minus'),
        ('left', 'multiply', 'divide'),
        ('right', 'uminus'),
    ]

    @token(r'[a-zA-Z_]\w*')
    def identifier(self, t):
        if t.value in self.keywords:
            t.name = t.value
        return True

    @token(r'\d+')
    def number(self, t):
        t.value = int(t.value)
        return True

    @token(r'\s+')
    def whitespace(self, t):
        return False

    @production('''
        statement : identifier '=' expression
    ''')
    def statement_assign(p):
        names[p[1]] = p[3]

    @production('''
        statement : expression
    ''')
    def statement_expr(p):
        print(p[1])

    @production('''
        expression : expression '+' expression
                   | expression '-' expression
                   | expression '*' expression
                   | expression '/' expression
    ''')
    def expression_binop(p):
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]

    @production('''
        expression : '-' expression %prec UMINUS
    ''')
    def expression_uminus(p):
        p[0] = -p[2]

    @production('''
        expression : '(' expression ')'
    ''')
    def expression_group(p):
        p[0] = p[2]

    @production('''
        expression : number
    ''')
    def expression_number(p):
        p[0] = p[1]

    @production('''
        expression : identifier
    ''')
    def expression_name(p):
        try:
            p[0] = names[p[1]]
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0


def main():
    # Build the parser
    from sply.parser import Parser

    grammar = Calc()
    parser = Parser(grammar)

    while True:
        try:
            data = raw_input('calc > ')
        except EOFError:
            break
        if data:
            parser.parse(data)


def test_lexer():
    # Just use lexer
    from sply.lex import Lexer

    grammar = Calc()
    lexer = Lexer()
    lexer.build(grammar)

    while True:
        try:
            data = raw_input('calc > ')
        except EOFError:
            break
        if data:
            lexer.parse(data)
            for tok in lexer.token():
                print(tok)


if __name__ == '__main__':
    main()
    # test_lexer()
