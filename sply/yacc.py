#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""SLR now, LALR(1) sooner."""


class YaccError(Exception):
    pass


class LRTable(object):
    def __init__(self):
        self.action = None
        self.goto = None


class Production(object):
    """Production in grammar-definition."""
    def __init__(self, name, rule, precedences, handler=None):
        self.name = name
        self.rule = rule
        self.precedences = precedences
        self.handler = handler

    def handle(self, t):
        if self.handler:
            self.handler(t)

    def validate(self):
        pass

    def __repr__(self):
        return '<Production({})>'.format(self.body)

    __str__ = __repr__


def split(rules):
    """Split `rules` to multiple Productions by lines."""
    return [rules]
    for rule in rules.splitlines():
        for part in rule.split():
            pass


class Yaccer(object):
    """Syntactic parser."""
    def __init__(self, lexer):
        self.lexer = lexer
        self.rules = ()

    def build(self, grammar):
        """Build syntactic rules according to `grammar`."""
        self.lexer.build(grammar)

        # self._make_rules(grammar)
        # self._validate_rules()

    def parse(self, data):
        self.lexer.parse(data)
        for tok in self.lexer.token():
            print(tok)

    def _make_rules(self, grammar):
        """Parse grammar to generate rules."""
        self.productions = []

        for method, rules in grammar.get_grammar_methods('production'):
            for rule in split(rules):
                _production = Production(
                    method.__name__,
                    rule,
                    grammar.precedences,
                    method
                )
                self.productions.append(_production)

    def _validate_productions(self):
        pass
