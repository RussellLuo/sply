#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sply.lex import Lexer
from sply.yacc import Yaccer


class Parser(object):
    """A controller of lexer and yaccer for convenience."""
    def __init__(self, grammar):
        lexer = Lexer()
        self.yaccer = Yaccer(lexer)
        self.yaccer.build(grammar)

    def parse(self, data):
        self.yaccer.parse(data)
