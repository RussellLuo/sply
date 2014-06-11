#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from operator import methodcaller
from collections import Counter, OrderedDict


class LexError(Exception):
    pass


class Rule(object):
    """Token rule defined in grammar."""
    def __init__(self, name, regex, handler=None):
        self.name = name
        self.regex = regex
        self.handler = handler

    def handle(self, t):
        if self.handler:
            self.handler(t)

    def priority(self):
        """Now only used for sorting purpose.

        1. In general, rules with handler are prior to those
           without handler
        2. Rules with handler are sorted by first-line-no of
           handler function
        3. Rules without handler are sorted by length of regex
        """
        if self.handler:
            return (1, self.handler.__code__.co_firstlineno)
        else:
            return (2, -len(self.regex))

    def validate(self):
        """Now only validate regular expression."""
        try:
            re.compile(self.regex)
        except re.error as e:
            raise LexError(str(e))

    def __repr__(self):
        return '<Rule({!r}, {!r})[{!s}]>'.format(self.name, self.regex,
                                                 self.priority())

    __str__ = __repr__


class Token(object):
    """Real token parsed from input by rules."""
    def __init__(self, name, value, position):
        self.name = name
        self.value = value
        self.position = position

    def __repr__(self):
        return 'Token<{}>: {!r}'.format(self.name, self.value)

    __str__ = __repr__


class Lexer(object):
    """Lexical parser.

    Usage:
        grammar = None  # The concrete Grammar you defined
        data = ''  # The language string
        lexer = Lexer()
        lexer.build(grammar)
        lexer.parse(data)
        for tok in lexer.token():
            print(tok)
    """
    def build(self, grammar, debug=True):
        """Build lexical rules according to `grammar`."""
        self._debug = debug

        self._make_rules(grammar)
        self._make_regex()

    def parse(self, data):
        assert isinstance(data, basestring)
        self._input = data

    def token(self):
        """yeild a token dynamically per call."""
        length = len(self._input)
        self.position = 0
        while self.position < length:
            # look for a regular expression match
            m = self._regex.match(self._input, self.position)
            if m:
                name = m.lastgroup
                value = m.group()
                tok = Token(name, value, self.position)
                self.position = m.end()

                rule = self._rules[name]
                handler = rule.handler
                if handler:
                    interested = handler(tok)
                    if not interested:
                        continue

                yield tok
            else:
                # nothing matched, see if in literals
                char = self._input[self.position]
                if char in self._literals:
                    tok = Token(char, char, self.position)
                    self.position += 1
                    yield tok
                else:
                    # non-literals, call error_handler instead
                    tok = Token('error', self._input[self.position],
                                self.position)
                    skip_chars = self._error_handler(tok)
                    if not skip_chars:
                        raise LexError('%s invalid input: "%s"' %
                                       (self.coordinate(tok), tok.value))
                    self.position += skip_chars

    def coordinate(self, tok):
        """ Calculate coordinate [line %s, column %s] from `tok.position`.

        `tok.position`: the offset from start of the parsed text

        Count the amount of newlines between the beginning of the parsed
        text and `position`. Then, count the column as an offset from
        the last newline.
        """
        num_newlines = self._input.count('\n', 0, tok.position)

        line_offset = self._input.rfind('\n', 0, tok.position)
        if line_offset < 0:
            line_offset = 0

        return '[line %s, column %s]' % (num_newlines + 1,
                                         tok.position - line_offset + 1)

    def _make_rules(self, grammar):
        """Parse grammar to generate rules."""
        self._error_handler = grammar.token_error_handler
        self._literals = grammar.literals

        # get rules from simple-tokens
        rules = [
            Rule(name, regex)
            for name, regex in grammar.simple_tokens
        ]

        # get rules from method-tokens
        for method, regex in grammar.get_grammar_methods('token'):
            rule = Rule(
                method.__name__,
                regex,
                method
            )
            rules.append(rule)

        if self._debug:
            # validate uniqueness
            rule_names = [rule.name for rule in rules]
            duplicates = [
                key
                for key, value in Counter(rule_names).items()
                if value > 1
            ]
            if duplicates:
                raise LexError('duplicated tokens: %s' % ', '.join(duplicates))

            # validate each rule
            for rule in rules:
                rule.validate()

        # sort by rule.priority()
        rules.sort(key=methodcaller('priority'))

        # get ordered-dict from `rules` list
        self._rules = OrderedDict([(rule.name, rule) for rule in rules])

    def _make_regex(self):
        regex = '|'.join([
            '(?P<%s>%s)' % (rule.name, rule.regex)
            for rule in self._rules.values()
        ])

        if self._debug:
            print('regex built from grammar: {!r}'.format(regex))

        self._regex = re.compile(regex)
