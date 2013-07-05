#!/usr/bin/env python
"""tag2html.py: Generates HTML from Tag instances
 This module
  - is the place where the HTML is generated.
"""
# backend
INDENT_SIZE = 4
bs4 = None

def indent(text, margin, function=lambda x:x):
    """Adds 'margin' to the beginning of every line in 'text'."""
    #Add an extra newline to the end of text. This ensures that any
    #existing trailing newline isn't lost.
    text += "\n"

    return '\n'.join((margin + x if function(x) else x)
                       for x in text.splitlines())

def _indent_ml_string(n, s):
    return indent(s, ' '*n*INDENT_SIZE)

def _at_indent(n, s):
    ''' return s, indented by n*INDENT_SIZE speces '''
    return ' '*n*INDENT_SIZE + s

def _try_to_import_bs4():
    global bs4
    try:
       import bs4
    except ImportError:
        try:
            import BeautifulSoup as bs4
        except ImportError:
            raise ImportError("BeautifulSoup needed for 'from_text'")

def get_html(obj):
    if isinstance(obj, PageElement):
        return obj.single_line_html()
    else:
        return unicode(obj)

def get_tag(obj):
    if bs4 and isinstance(obj, bs4.Tag):
        return Tag(from_text=unicode(obj))
    elif isinstance(obj, Tag):
        return obj
    else:
        return unicode(obj)

# an empty class from which all page-elements "have" to inherit...
class PageElement(object):
    pass

class Tag(PageElement):
    """ An Html tag """
    def __init__(self, name='', closing=False, **attrs):
        # Ensure that name is a string and handling, case-insensitive
        self.name = name.lower()
        self._contents = []
        self.closing = closing
        if 'Class' in attrs:
            attrs['class'] = attrs['Class']

        if attrs.get('from_text'):
            if bs4 is None:
                _try_to_import_bs4()
            self.extract_from(bs4.BeautifulSoup(attrs['from_text']))
        else:
            self._attrs = attrs

    def __repr__(self):
        return "{0.__class__.__name__}: {0.name}".format(self)

    def __iter__(self):
        return iter(self._contents)

    def __nonzero__(self):
        return bool(self._contents or self._attrs)

    def extract_from(self, soup):
        # get the tag
        try:
            tag = soup.html.children.next().children.next()
        except:
            raise
            raise ValueError('Unable to get data')

        # place the required atttributes
        self._contents = map(get_tag, tag.children)
        self.name = tag.name
        self._attrs = tag.attrs

    def single_line_html(self):
        if self.name == 'br':
            return '<br/>'
        attrs = ''
        for k,v in self._attrs.iteritems():
            attrs += ' '+'{0}={1!r}'.format(k,v)
        if self.closing:
            return "<{0}{1}/>".format(self.name, attrs)
        inner_html = ''.join(map(get_html, self._contents))
        return "<{0}{1}>{2}</{0}>".format(self.name, attrs,
                                          inner_html).replace('\n','')

    def html(self):
        return self._beauty_html(0)

    def _beauty_html(self, indent): # backend
        attrs = ''
        for k,v in self._attrs.iteritems():
            attrs += ' '+'{0}={1!r}'.format(k,v)
        if self.closing:
            return _at_indent(indent, "<{0}{1}/>".format(self.name, attrs))
        retval = _at_indent(indent, "<{0}{1}>".format(self.name, attrs))
        new_line = False
        if not self._contents:
            return retval + "</{0}>".format(self.name)
        else:
            for i in self._contents:
                if isinstance(i, Tag):
                    if i.name != 'br':
                        retval += '\n'+i._beauty_html(indent+1)
                    else:
                        # maintain consistency!!
                        retval += '<br/>'
                else:
                    retval += '\n' + _indent_ml_string(indent+1, i)

            if '\n' in retval:
                retval = retval.rstrip() + '\n' + _at_indent(indent, '')

        retval += "</{0}>".format(self.name)
        return retval

    def add_child(self, child):
        """ Add a child, Tag or string """
        if self.closing:
            raise AttributeError('cannot add child to self-closing tag')
        elif isinstance(child, (PageElement, basestring)):
            self._contents.append(child)
        else:
            raise TypeError("'child' should be a PageElement or a string,"
                            "not {0}".format(child.__class__.__name__))

    def add_tag(self, name='', closing=False, **attrs):
        if self.closing:
            raise AttributeError('cannot add child to self-closing tag')
        tag = Tag(name, closing, **attrs)
        self._contents.append(tag)
        return tag

    def to_ptml(self):
        return self._to_ptml(0)

    def _to_ptml(self, indent): # backend
        s = self.name
        for k,v in self._attrs.iteritems():
            s += ' {0}={1!r}'.format(k,v)
        s += ':'
        retval = _at_indent(indent, s)+'\n'
        if not self._contents:
            retval += _at_indent(indent+1,'pass')
            return retval
        for i in self._contents:
            if isinstance(i, Tag):
                if i.name != 'br':
                    retval += i._to_ptml(indent+1)+'\n'
                else:
                    retval = retval[:-1]
                    retval += '<br/>\n'
            else:
                 retval += _indent_ml_string(indent+1, repr(str(i)))+'\n'
        return retval.rstrip('\n')


class Html(PageElement):
    def __init__(self):
        super(Html, self).__init__()
        self.body = Tag('body')
        self.head = Tag('head')

    def html(self, doctype_data=None):
        base_tag = Tag('html')
        # add the containers
        if self.head:
            base_tag.add_child(self.head)
        if self.body:
            base_tag.add_child(self.body)
        retval = base_tag.html()
        if doctype_data is None:
            return retval
        else:
            return '\n'.join(doctype_data, retval)

class Page(object):
    def __init__(self):
        self.title = ''
        self.scripts = []
        self.styles = []
        self.body = []

    def add_child(self, child):
        if isinstance(child, (PageElement, basestring)):
            if isinstance(child, Tag):
                if child.name == 'script':
                    self.scripts.append(child)
                elif child.name == 'style':
                    self.styles.append(child)
                else:
                    self.body.append(child)
            else:
                self.body.append(child)
        else:
            raise TypeError("'child' should be a PageElement or a string, not {0}"
                            .format(child.__class__.__name__))

    def add_tag(self, name='', closing=False, **attrs):
        tag = Tag(name, closing, **attrs)
        self.add_child(tag)
        return tag

    def html(self):
        parent = Html()
        title = []
        if self.title:
            title_tag = Tag('title')
            title_tag.add_child(self.title)
            title.append(title_tag)

        for i in title + self.scripts + self.styles:
            parent.head.add_child(i)
        for i in self.body:
            parent.body.add_child(i)

        return parent.html()

# Convienience classes
class Link(Tag):
    def __init__(self, text, href, **attrs):
        super(self.__class__, self).__init__('a', href=href, **attrs)
        self.add_child(text)

class Image(Tag):
    def __init__(self, text, src, **attrs):
        super(self.__class__, self).__init__('img', True, src=src,
                                             alt=text, **attrs)

class TagGenerator(object):
    def __getattr__(self, name):
        return Tag(name)

if __name__ == '__main__':
    li = '<ul><li>abc</li><li>abcd</li></ul>'
    h = Tag(from_text=li)
