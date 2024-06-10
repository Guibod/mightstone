from unittest import TestCase

from mightstone.services.wiki.models import WikiString, WikiTag


class WikiStringTest(TestCase):
    def test_simple(self):
        string = WikiString(tokens=["foo bar baz"])

        self.assertEqual(str(string), "foo bar baz")

    def test_splitted(self):
        string = WikiString(tokens=["foo", "bar", "baz"])

        self.assertEqual(str(string), "foo bar baz")

    def test_with_tag(self):
        string = WikiString(tokens=["foo", WikiTag(tag="bar"), "baz"])

        self.assertEqual(str(string), "foo {{ bar }} baz")

    def test_with_hyperlink(self):
        string = WikiString(tokens=["foo [bar] baz"])

        self.assertEqual(str(string), "foo bar baz")

    def test_with_html_entities(self):
        string = WikiString(tokens=["foo &lt;bar&gt; baz"])

        self.assertEqual(str(string), "foo <bar> baz")


class WikiTagTest(TestCase):
    def test_simple(self):
        tag = WikiTag(tag="foo")

        self.assertEqual(str(tag), "{{ foo }}")

    def test_with_extra(self):
        tag = WikiTag(tag="foo", extra=WikiString.from_string("bar baz"))

        self.assertEqual(str(tag), "{{ foo bar baz }}")

    def test_with_args(self):
        tag = WikiTag(
            tag="foo",
            args=[WikiString.from_string("bar"), WikiString.from_string("baz")],
        )

        self.assertEqual(str(tag), "{{ foo | bar | baz }}")

    def test_with_kwargs(self):
        tag = WikiTag(
            tag="foo",
            kwargs={
                "bar": WikiString.from_string("1"),
                "baz": WikiString.from_string("qux"),
            },
        )

        self.assertEqual(str(tag), "{{ foo | bar = 1 | baz = qux }}")

    def test_with_everything(self):
        tag = WikiTag(
            tag="foo",
            args=[WikiString.from_string("bar"), WikiString.from_string("baz")],
            kwargs={
                "qux": WikiString.from_string("1"),
                "quux": WikiString.from_string("corge"),
            },
        )

        self.assertEqual(str(tag), "{{ foo | bar | baz | qux = 1 | quux = corge }}")
