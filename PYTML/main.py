#!/usr/bin/env python
""" main.py: User Interface module
 This module
  - Gives user access to what he/she may need from this package.
  - Exposes the command line, so that the user can use it for compiling or
    debugging his PTML code.
 """
from tag2html import Tag
from ptml_parser import to_tag
from tokenizer import tokenize

# Main Conversion Functions
def get_HTML(obj):
    if isinstance(obj, list):
        if all(map(lambda x: isinstance(x, Tag), obj)):
            return '\n'.join(map(get_HTML, obj))
    elif isinstance(obj, Tag):
        return obj.html()
    return get_HTML(get_tag(obj))  # try to recursively get tag

def get_tag(obj):
    if hasattr(obj, '__next__') or hasattr(obj, 'next'):
        return to_tag(list(obj))
    elif hasattr(obj, '__iter__'):
        return to_tag(iter(obj))
    else:
        return get_tag(get_tokens(obj))  # try to recursively get tokens

def get_tokens(obj):
    if isinstance(obj, basestring):
        return tokenize(obj)
    elif isinstance(obj, file):
        return tokenize(obj)
    else:
        # object not valid
        raise TypeError('Got unexpected object type {0!r}'.format(
            obj.__class__.__name__))

get_html = get_HTML

def from_html(html):
    return Tag(from_text=html).ptml()

# Interpretter
class Interpretter(object):
    def __init__(self):
        super(Interpretter, self).__init__()
        self.prompt1 = 'pytml > '
        self.prompt2 = '....... '
        self.func = get_html

    def continue_line(self, line):
        return bool(line)

    def run_once(self):
        try:
            s = ''
            line = raw_input(self.prompt1)
            while self.continue_line(line):
                s += line+'\n'
                line = raw_input(self.prompt2)
            s += line+'\n'
            self.run(s)
        except KeyboardInterrupt:
            pass

    def run_prompt(self):
        while True:
            self.run_once()

    def run(self, text):
        if text == "html":
            self.func = get_html
        elif text == "tag":
            self.func = get_tag
        elif text == "token":
            def print_tokens(text):
                for i in get_tokens(text):
                    print i
            self.func = print_tokens
        else:
            try:
                print self.func(text)
                print '------'
            except Exception, e:
                print e
if __name__ == '__main__':
    Interpretter().run_prompt()
