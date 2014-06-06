#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ### decorators ###

def token(regex):
    def wrapper(func):
        func.grammar = {
            'type': 'token',
            'definition': regex
        }
        return func
    return wrapper


def production(rules):
    def wrapper(func):
        func.grammar = {
            'type': 'production',
            'definition': rules
        }
        return func
    return wrapper


class Grammar(object):
    """Grammar-definition."""

    simple_tokens = ()
    precedences = ()

    def token_error_handler(self, t):
        """Error handler when parsing tokens.

        Return value:
            the number of characters should be skipped
            to try parsing the next token.

            0 -- no skip (terminate the current parsing process)
        """
        print('Illegal characters "%s"' % t.value)
        return 1

    def production_error_handler(self, p):
        if p:
            print('Syntax error at %s' % p.value)
        else:
            print('Syntax error at EOF')

    @token(r'\n+')
    def newline(self, t):
        t.lineno += t.value.count('\n')
        return False

    @token(r' |\t')
    def whitespace(self, t):
        return False

    def get_grammar_methods(self, grammar_type):
        methods = []

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            grammar = getattr(attr, 'grammar', None)
            if grammar and grammar['type'] == grammar_type:
                methods.append((attr, grammar['definition']))

        return methods
