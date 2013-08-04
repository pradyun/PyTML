#!/usr/bin/env python
"""parser.py: Generates the Tag tree from tokens
 This module
  - parses the tokens into a Tag structure using LR technique
"""

import re
import cgi  # escaping
from textwrap import dedent
from tag2html import Tag
from tokenizer import tokenize


def to_tag(tokens):
    return Parser().parse(tokens)


def escape_string(text):
    return cgi.escape(str(text)).encode('ascii', 'xmlcharrefreplace')

class Parser:

    def __init__(self):
        self.current = None
        self.tokens = []
        self.index = None

    def get_token(self, end_expected=False):
        try:
            retval = self.tokens[self.index]
        except IndexError:
            if end_expected:
                return None
            raise
        else:
            return retval

    def next_token(self, end_expected=False):
        self.index += 1
        return self.get_token(end_expected)

    def check_if(self, typeof, values=None, msg_type='', msg_values=''):
        "Check the type and value of the next token"
        token = self.next_token()
        while token.type in ['COMMENT', 'NL', 'NEWLINE']:
            token = self.next_token()

        # check type
        if token.type not in typeof:
            raise SyntaxError("Expected " +\
                        (msg_type + " got {token.type}").format(token=token))

        # check value if needed
        if values is not None and token.value not in values:
            raise SyntaxError("Expected " + msg_values.format(token=token))

    def parse(self, tokens):
        self.tokens = list(tokens)
        del tokens
        self.index = 0
        base = []
        while self.index < len(self.tokens):
            x = self.parse_token()
            if x is not None:
                base.append(x)
            self.index += 1
        return base

    def parse_token(self):
        token = self.get_token()

        typ = token.type  # save some typing

        if typ in ['NEWLINE','NL','INDENT', 'COMMENT', "DEDENT"]:
            return
        elif typ == 'NAME':
            if token.value == 'pass':
                return
            return self.parse_tag()
        elif typ == 'BREAK':
            return Tag('br')
            # return {'name':'br','attrs':{},'children':[]}
        elif typ in ['STRING']:
            return self.parse_string()
        elif typ in ['NEWLINE','NL','INDENT']:
            return
        else:
            pass
            #print token

    def parse_string(self):
        escape = True
        value = self.get_token().value
        if value[0] == 'r':
            escape = False
            value = value[1:]
        s = eval(value)
        s = dedent(s)
        if escape:
            s = escape_string(s)
        return s.strip('\r\n')

    def parse_tag(self):
        token = self.get_token()
        if token.type == 'NAME':
            name = token.value
        else:
            raise SyntaxError

        # move through the attributes
        attrs = self.get_attributes()

        check_if = self.check_if
        check_if(["OP"]     , [":"], "a colon", "a colon")
        # check_if(["NEWLINE"], None , "a newline") | newline is ignored
        check_if(["INDENT"] , None , "indent")

        # make tag, ready for children
        tag = Tag(name, **attrs)

        token = self.next_token()
        # empty body
        if (token.type == 'NAME' and token.value.lower() == 'pass'):
            index = self.index
            while token.type in ['NEWLINE','NL','INDENT', 'COMMENT']:
                token = self.next_token()
            if token.type == 'DEDENT':
                return tag
            else:
                self.index = index

        # get children
        while token.type not in ['DEDENT', 'ENDMARKER']:
            x = self.parse_token()
            if x is not None:
                tag.add_child(x)
            token = self.next_token(True)

        return tag

    def get_attributes(self):
        check_if = self.check_if
        token = self.get_token()
        di = {}
        while (self.tokens[self.index+1]).type != 'OP':  # next not colon
            # name
            check_if(["NAME"], None, "a name")
            key = self.get_token().value
            if key == 'pass':
                return di
            # equal
            check_if(["OP"] , ["="], "'='", "'='")
            # string
            check_if(["STRING"], None, "a string")
            di[key] = self.parse_string()

        return di


if __name__ == '__main__':
    text = open('test.ptml').read()
    p = Parser()
    toks = list(tokenize(text))
    h = p.parse(toks)[0]
    print h
