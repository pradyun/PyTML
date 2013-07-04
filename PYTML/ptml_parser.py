import re
from textwrap import dedent
from tag2html import Tag
from tokenizer import tokenize, tokens


def to_tag(tokens):
    return Parser().parse(tokens)


class ParseError(Exception):
    def __str__(self):
        return '{self.__class__.__name__}: {self.msg}'


class ParseSyntaxError(ParseError, SyntaxError):
    pass


class Parser:

    def __init__(self):
        self.current = None
        self.tokens = []
        self.index = None

    def get_token(self, end_expected=False):
        try:
            return self.tokens[self.index]
        except IndexError:
            if end_expected:
                return None
            raise

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

        if typ == 'TAG':
            return self.parse_tag()
        elif typ == 'BREAK':
            return Tag('br')
            # return {'name':'br','attrs':{},'children':[]}
        elif typ in ['STRING', 'ML_STRING']:
            return self.parse_string(typ == 'ML_STRING')
        elif typ in ['NEWLINE', 'INDENT']:
            return
        else:
            print token

    def parse_string(self, ml=False):
        s = eval(self.get_token().value)
        if ml:
            s = dedent(s)
        return s.strip()

    def parse_tag(self):
        token = self.get_token()

        # retval = {'name':None,
        #          'attrs':{},
        #          'children':[]}

        text = token.value[:-1]  # remove the colon ':' at the end

        if ' ' in text:  # there are attributes
            name, attrs = re.split('\s+', text, 1)
            attrs = map(lambda x: x.split('='),
                        re.split('\s+', attrs))
            attrs = {k: v for k, v in attrs}
        else:
            name = text
            attrs = {}

        # retval['name'] = name
        # retval['attrs'] = attrs
        tag = Tag(name, **attrs)

        self.index += 1
        token = self.get_token()

        if (token.type == 'NAME' and token.value.lower() == 'pass'):
            return tag
        #    return retval
        elif token.type == 'STRING':
            x = self.parse_token()
            if x is not None:
                # children.append(x)
                tag.add_child(x)
            return tag
        elif token.type == 'NEWLINE':
            pass
        else:
            raise Exception('ParseError: expected newline or pass')

        self.index += 1
        token = self.get_token()

        if token.type != 'INDENT':
            raise Exception('ParseError: Expected indent')

        self.index += 1
        token = self.get_token()
        if (token.type == 'NAME' and token.value.lower() == 'pass'):
            return tag
            # return retval

        # get children
        # children = []
        while token != None and token.type != 'DEDENT':
            x = self.parse_token()
            if x is not None:
                # children.append(x)
                tag.add_child(x)

            self.index += 1
            token = self.get_token(True)

        # retval['children'] = children
        # return retval
        return tag

if __name__ == '__main__':
    text = """
html:
    head:
        script src='href': pass
    body:
        p:
            "Hello World" <br/>
            '''
            This is multiline
            String :)
            '''
    """
    p = Parser()
    toks = list(tokenize(text))
    h = p.parse(toks)[0]
    print text
    print '-' * 40
    print h
    print h.to_ptml()
