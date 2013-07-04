""" main.py: User Interface module
 This module gives the user access to the stuff he may need and this package
 can provide. It also exposes the command line, so that the user can use it
 for compiling or debugging his PTML code.
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
    return get_HTML(get_tag(obj))  # try to get tag


def get_tag(obj):
    if hasattr(obj, '__next__') or hasattr(obj, 'next'):
        return to_tag(list(obj))
    elif hasattr(obj, '__iter__'):
        return to_tag(iter(obj))
    else:
        return get_tag(get_tokens(obj))  # try to get tokens


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


def interface_command_line():
    import argparse
    import sys

if __name__ == '__main__':
    interface_command_line()