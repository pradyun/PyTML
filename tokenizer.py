import sys, traceback
import lex

__all__ = ['tokenize']
tokens = [
    'TAG',
    'PASS',
    'NEWLINE',
    'NAME',
    'EQUAL',
    'NUMBER',
    'STRING',
    'ML_STRING',
    'INDENT',
    'DEDENT',
    'COMMENT',
    'BREAK',
         ]

t_NAME = r"[a-zA-z]+"
t_STRING = r'("[^\\\\n\"]+"' '|' r"'[^\\\\n\']+')"
t_NUMBER = r"[-+]?\d*\.\d+|\d+\.|\d+"
#t_ML_STRING  = r'("""[^\\]+"""' '|' r"'''[^\\]+''')"
t_COMMENT = r"\#.*"
t_BREAK = r"\</?[b|B][r|R]/?\>"
t_TAG = r'{name}(\s+{name}\s*=\s*{string})*:'.format(name=t_NAME,
                                                  string=t_STRING)
# Manage line-no
def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += len(t.value)
    return t

def t_ML_STRING(t):
    t.lexer.lineno += t.value.count('\n')
    return t
t_ML_STRING.__doc__ = r'("""[^\\]+"""' '|' r"'''[^\\]+''')"

indents = [0]
def t_INDENT(t):
    ## Manages indents and dedents
    r"(^|(?<=\s))\s+"
    global indents
    column = t.value
    # count indents or dedents
    if column > indents[-1]:
        indents.append(column)
        return t
    elif column < indents[-1]:
        no_of_dedents = 0
        last_indent = indents[-1]
        while column < indents[-1]:
            if column not in indents:
                line = t.lexer.lexdata.splitlines()[t.lexer.lineno-1]
                linepos = line.find(t.value)
                msg = "unindent does not match any outer indentation level"
                fname = '<parser>'
                raise IndentationError(msg, (fname, t.lineno, linepos, line))
            indents = indents[:-1]
            no_of_dedents += 1
        t.type = 'DEDENT'
        t.value = ' '*(len(last_indent) - len(t.value))
        t.count = no_of_dedents
        return t

# Error handling rule
def t_error(t):
    if t.value[0] != ' ':
        print " Illegal character: {0!r} ".format(t.value[0]).center(30, '*')
    t.lexer.skip(1)

def tokenize(text):
    lexer = lex.lex()
    lexer.input(text)
    return lexer

if __name__ == '__main__':
    text = """
html:
    head:
        script src='href':
            pass
    body:
        p:
            "Hello World" <br/>
            '''
            Yo yo honey
            singh
            '''
"""
    print text
    print '-'*40
    for i in tokenize(text):
        print i
    del i
