import StringIO
import tokenize as tokenizer

def tokenize(text):
    if not hasattr(text, 'readline'):
        readline = StringIO.StringIO(text).readline
    else:
        readline = text.readline
    for token in tokenizer.generate_tokens(readline):
        yield Token(*token)


class Token(object):
    """A convenience class for handling tokens"""
    def __init__(self, typ, value, srow_scol, erow_ecol, line):
        super(Token, self).__init__()
        self.type = tokenizer.tok_name[typ]
        self.srow, self.scol = srow_scol
        self.erow, self.ecol = erow_ecol
        self.line = line
        self.value = value
        assert isinstance(self.type, basestring), "Expected 'typ' to be string"
        assert isinstance(line, basestring), "Expected 'line' to be string"
        assert all(map(lambda i: isinstance(i, int),
                       [self.erow, self.ecol,
                        self.srow, self.scol])), "Expected integers"
    def __repr__(self):
        return  ("{self.__class__.__name__}(" +\
                "{self.type}, {self.srow}-{self.scol}, "+\
                "{self.erow}-{self.ecol}, {self.value!r})").format(self=self)

if __name__ == '__main__':
    text = open('test.ptml').read()
    for i in tokenize(text):
        print i



