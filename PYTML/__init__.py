#!/usr/bin/env python
"""PYTML: Pythonic Text Markup Language
PYTML is a small language that compiles into HTML
"""

from main import get_HTML, get_tag, get_tokens

if __name__ == '__main__':
    text = open("test.ptml").read()
    html = get_HTML(text)
    with open("test.html", 'w') as f:
        f.write(html)
