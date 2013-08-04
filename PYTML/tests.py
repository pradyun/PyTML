import main
import unittest


class HTMLTestCase(unittest.TestCase):

    def setUp(self):
        self.expected = """
            <html>
                <head>
                    <script src='foo.js'></script>
                </head>
                <body>
                    <p>
                        Hello World!!
                    </p>
                </body>
            </html>""".strip()

    def striplines(self, string):
        return '\n'.join(map(lambda x: x.strip(), string.splitlines()))

    def test_ptml_to_html(self):
        html = main.get_html("""
            html:
                head:
                    script src="foo.js": pass
                body:
                    P:
                        "Hello World!!"
            """)
        self.assertIsInstance(html, basestring, msg="message")
        self.assertEqual(self.striplines(html), self.striplines(self.expected),
                         msg="values don't match expected")

    def test_tag_to_html(self):
        tag_html = main.Tag('html')
        tag_head = main.Tag('head')
        tag_body = main.Tag('body')
        tag_script = main.Tag('script', src='foo.js')
        tag_p = main.Tag('P')
        tag_head.add_child(tag_script)
        tag_p.add_child("Hello World!!")
        tag_body.add_child(tag_p)
        tag_html.add_child(tag_head)
        tag_html.add_child(tag_body)

        html = main.get_html(tag_html)
        self.assertIsInstance(html, basestring, msg="message")
        self.assertEqual(self.striplines(html), self.striplines(self.expected))


class TagTestCase(unittest.TestCase):

    def setUp(self):
        self.ptml = """
        ul foo='bar':
            li:
               'abc'
            li:
               'abcd'""".strip()

    def striplines(self, string):
        return '\n'.join(map(lambda x: x.strip(), string.splitlines()))

    def test_ptml2tag2ptml(self):
        tag_generated = main.get_tag(self.ptml)[0]
        self.assertEqual(self.striplines(self.ptml), self.striplines(tag_generated.to_ptml()))

if __name__ == '__main__':
    unittest.main()
