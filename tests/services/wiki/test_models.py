import datetime
import textwrap
from pathlib import Path
from unittest import TestCase

import bs4
import pytest
from assertpy import assert_that
from pydantic_core import Url

from mightstone.services.wiki.models import (
    WikiFlow,
    WikiHtml,
    WikiLink,
    WikiList,
    WikiListItem,
    WikiListItemStyle,
    WikiListStyle,
    WikiPage,
    WikiParagraph,
    WikiString,
    WikiStyledText,
    WikiTemplate,
    WikiTextStyle,
    WikiTitle,
)


class TestWikiPage:
    def test_fail_factory(self):
        with pytest.raises(TypeError):
            WikiPage.from_tag(bs4.Tag(name="page"), "https://example.com")

    def test_factory(self):
        data = Path(__file__).parent.joinpath("samples/affinity.xml").read_bytes()
        soup = bs4.BeautifulSoup(data, "lxml")
        page = WikiPage.from_tag(soup.find("page"), "https://example.com")

        assert_that(page).is_instance_of(WikiPage)
        assert_that(page.id).is_equal_to(3155)
        assert_that(page.title).is_equal_to("Affinity")
        assert_that(page.url).is_equal_to(Url("https://example.com/wiki/Affinity"))
        assert_that(page.revisions).is_length(1)
        assert_that(page.revisions[0].id).is_equal_to(519489)
        assert_that(page.revisions[0].parent_id).is_equal_to(512778)
        assert_that(page.revisions[0].timestamp).is_equal_to(
            datetime.datetime(
                year=2024,
                month=5,
                day=12,
                hour=12,
                minute=48,
                second=25,
                tzinfo=datetime.timezone.utc,
            )
        )
        assert_that(page.revisions[0].contributor_name).is_equal_to("Hunterofsalvation")
        assert_that(page.revisions[0].contributor_id).is_equal_to(40376267)
        assert_that(page.revisions[0].origin).is_equal_to(519489)
        assert_that(page.revisions[0].source).starts_with("{{Infobox keyword")


@pytest.fixture
def wiki_string():
    return WikiString(text="foo bar baz")


@pytest.fixture
def wiki_title_level_1():
    return WikiTitle(title="Lorem Ipsum", level=1)


@pytest.fixture
def wiki_title_level_3():
    return WikiTitle(title="Sin Dolore", level=3)


@pytest.fixture
def wiki_html_link():
    return WikiHtml(
        tag="a",
        attributes={"href": "https://example.com", "class": "visited"},
        content=WikiString(text="example.com"),
    )


@pytest.fixture
def wiki_html_ref_eztumbler():
    return WikiHtml(
        tag="ref",
        content=WikiTemplate(
            name="EzTumbler",
            args=[
                WikiString(
                    text="https://markrosewater.tumblr.com/post/707260642788327424"
                ),
                WikiString(text="January 23, 2023"),
            ],
            kwargs={"Title": WikiString(text="Is affinity deciduous now?")},
        ),
    )


@pytest.fixture()
def wiki_bold_text():
    return WikiStyledText(
        content=WikiString(text="bold text"), style=WikiTextStyle.BOLD
    )


@pytest.fixture()
def wiki_italic_text():
    return WikiStyledText(
        content=WikiString(text="italic text"), style=WikiTextStyle.ITALIC
    )


@pytest.fixture()
def wiki_bold_and_italic_text():
    return WikiStyledText(
        content=WikiString(text="bold and italic text"), style=WikiTextStyle.ITALIC_BOLD
    )


@pytest.fixture()
def wiki_no_style_text():
    return WikiStyledText(
        content=WikiString(text="no style whatsoever"), style=WikiTextStyle.NONE
    )


@pytest.fixture()
def wiki_link_simple():
    return WikiLink(text="Mark Rosewater", url="Mark Rosewater")


@pytest.fixture()
def wiki_link_labeled():
    return WikiLink(text="Example", url="https://example.com")


@pytest.fixture()
def wiki_empty_flow():
    return WikiFlow()


@pytest.fixture()
def wiki_flow(wiki_italic_text, wiki_link_labeled, wiki_string):
    return WikiFlow(items=[wiki_italic_text, wiki_link_labeled, wiki_string])


@pytest.fixture()
def wiki_list_simple():
    return WikiList(
        level=0,
        style=WikiListStyle.NUMBERED,
        items=[
            WikiListItem(
                level=1,
                style=WikiListItemStyle.NUMBERED,
                content=WikiString(text="one"),
            ),
            WikiListItem(
                level=1,
                style=WikiListItemStyle.NUMBERED,
                content=WikiString(text="two"),
            ),
            WikiListItem(
                level=1,
                style=WikiListItemStyle.NUMBERED,
                content=WikiString(text="three"),
            ),
        ],
    )


@pytest.fixture()
def wiki_list_nested():
    return WikiList(
        level=0,
        style=WikiListStyle.BULLET,
        items=[
            WikiListItem(
                level=1, style=WikiListItemStyle.BULLET, content=WikiString(text="one")
            ),
            WikiList(
                level=1,
                style=WikiListStyle.DEF,
                items=[
                    WikiListItem(
                        level=2,
                        style=WikiListItemStyle.TERM,
                        content=WikiString(text="definition term"),
                    ),
                    WikiListItem(
                        level=2,
                        style=WikiListItemStyle.DEFINITION,
                        content=WikiString(text="definition one"),
                    ),
                    WikiListItem(
                        level=2,
                        style=WikiListItemStyle.DEFINITION,
                        content=WikiString(text="definition two"),
                    ),
                    WikiList(
                        level=2,
                        style=WikiListStyle.NUMBERED,
                        items=[
                            WikiListItem(
                                level=3,
                                style=WikiListItemStyle.NUMBERED,
                                content=WikiString(text="two four one"),
                            ),
                            WikiListItem(
                                level=3,
                                style=WikiListItemStyle.NUMBERED,
                                content=WikiString(text="two four two"),
                            ),
                            WikiListItem(
                                level=3,
                                style=WikiListItemStyle.NUMBERED,
                                content=WikiString(text="two four three"),
                            ),
                        ],
                    ),
                ],
            ),
            WikiListItem(
                level=1,
                style=WikiListItemStyle.BULLET,
                content=WikiString(text="three"),
            ),
            WikiListItem(
                level=1,
                style=WikiListItemStyle.BULLET,
                content=WikiString(text="four"),
            ),
        ],
    )


@pytest.fixture()
def wiki_paragraph(wiki_list_simple):
    return WikiParagraph(
        items=[
            WikiString(
                text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur placerat malesuada maximus."
            ),
            WikiString(
                text="Nullam eleifend arcu commodo, sollicitudin neque non, ornare sapien. Vestibulum eros lacus, volutpat sit amet metus ut, varius imperdiet diam."
            ),
            wiki_list_simple,
            WikiString(
                text="Ut ac augue sed metus cursus pretium id ut risus. Donec rhoncus dignissim metus in venenatis."
            ),
        ]
    )


class TestWikiString:
    def test_as_text(self, wiki_string):
        assert_that(wiki_string.as_text()).is_equal_to("foo bar baz")

    def test_as_wiki(self, wiki_string):
        assert_that(wiki_string.as_wiki()).is_equal_to("foo bar baz")

    def test_as_html(self, wiki_string):
        assert_that(wiki_string.as_html()).is_equal_to("foo bar baz")


class TestWikiTitleLevel1:
    def test_as_text(self, wiki_title_level_1):
        assert_that(wiki_title_level_1.as_text()).is_equal_to("Lorem Ipsum")

    def test_as_wiki(self, wiki_title_level_1):
        assert_that(wiki_title_level_1.as_wiki()).is_equal_to("\n\n== Lorem Ipsum ==\n")

    def test_as_html(self, wiki_title_level_1):
        assert_that(wiki_title_level_1.as_html()).is_equal_to("\n<h1>Lorem Ipsum</h1>")


class TestWikiTitleLevel3:
    def test_as_text(self, wiki_title_level_3):
        assert_that(wiki_title_level_3.as_text()).is_equal_to("Sin Dolore")

    def test_as_wiki(self, wiki_title_level_3):
        assert_that(wiki_title_level_3.as_wiki()).is_equal_to(
            "\n\n==== Sin Dolore ====\n"
        )

    def test_as_html(self, wiki_title_level_3):
        assert_that(wiki_title_level_3.as_html()).is_equal_to("\n<h3>Sin Dolore</h3>")


class TestWikiHtmlLink:
    def test_as_text(self, wiki_html_link):
        assert_that(wiki_html_link.as_text()).is_equal_to("example.com")

    def test_as_wiki(self, wiki_html_link):
        assert_that(wiki_html_link.as_wiki()).is_equal_to(
            '<a href="https://example.com" class="visited">example.com</a>'
        )

    def test_as_html(self, wiki_html_link):
        assert_that(wiki_html_link.as_html()).is_equal_to(
            '<a href="https://example.com" class="visited">example.com</a>'
        )


class TestWikiHtmlRefEzTumbler:
    def test_as_text(self, wiki_html_ref_eztumbler):
        assert_that(wiki_html_ref_eztumbler.as_text()).is_equal_to("")

    def test_as_wiki(self, wiki_html_ref_eztumbler):
        assert_that(wiki_html_ref_eztumbler.as_wiki()).is_equal_to(
            "<ref>{{ EzTumbler | https://markrosewater.tumblr.com/post/707260642788327424 | January 23, 2023 | Title = Is affinity deciduous now? }}</ref>"
        )

    def test_as_html(self, wiki_html_ref_eztumbler):
        assert_that(wiki_html_ref_eztumbler.as_html()).is_equal_to("<ref></ref>")


class TestWikiStyledTextBold:
    def test_as_text(self, wiki_bold_text):
        assert_that(wiki_bold_text.as_text()).is_equal_to("bold text")

    def test_as_wiki(self, wiki_bold_text):
        assert_that(wiki_bold_text.as_wiki()).is_equal_to("'''bold text'''")

    def test_as_html(self, wiki_bold_text):
        assert_that(wiki_bold_text.as_html()).is_equal_to("<b>bold text</b>")


class TestWikiStyledTextItalic:
    def test_as_text(self, wiki_italic_text):
        assert_that(wiki_italic_text.as_text()).is_equal_to("italic text")

    def test_as_wiki(self, wiki_italic_text):
        assert_that(wiki_italic_text.as_wiki()).is_equal_to("''italic text''")

    def test_as_html(self, wiki_italic_text):
        assert_that(wiki_italic_text.as_html()).is_equal_to("<i>italic text</i>")


class TestWikiStyledTextItalicBold:
    def test_as_text(self, wiki_bold_and_italic_text):
        assert_that(wiki_bold_and_italic_text.as_text()).is_equal_to(
            "bold and italic text"
        )

    def test_as_wiki(self, wiki_bold_and_italic_text):
        assert_that(wiki_bold_and_italic_text.as_wiki()).is_equal_to(
            "'''''bold and italic text'''''"
        )

    def test_as_html(self, wiki_bold_and_italic_text):
        assert_that(wiki_bold_and_italic_text.as_html()).is_equal_to(
            "<b><i>bold and italic text</i></b>"
        )


class TestWikiLinkSimple:
    def test_as_text(self, wiki_link_simple):
        assert_that(wiki_link_simple.as_text()).is_equal_to("Mark Rosewater")

    def test_as_wiki(self, wiki_link_simple):
        assert_that(wiki_link_simple.as_wiki()).is_equal_to("[[Mark Rosewater]]")

    def test_as_html(self, wiki_link_simple):
        assert_that(wiki_link_simple.as_html()).is_equal_to(
            '<a href="Mark Rosewater">Mark Rosewater</a>'
        )


class TestWikiLinkLabeled:
    def test_as_text(self, wiki_link_labeled):
        assert_that(wiki_link_labeled.as_text()).is_equal_to("Example")

    def test_as_wiki(self, wiki_link_labeled):
        assert_that(wiki_link_labeled.as_wiki()).is_equal_to(
            "[[Example|https://example.com]]"
        )

    def test_as_html(self, wiki_link_labeled):
        assert_that(wiki_link_labeled.as_html()).is_equal_to(
            '<a href="https://example.com">Example</a>'
        )


class WikiTemplateTest(TestCase):
    def test_simple(self):
        tag = WikiTemplate(name="foo")

        self.assertEqual(tag.as_text(), "")
        self.assertEqual(tag.as_wiki(), "{{ foo }}")

    def test_with_extra(self):
        tag = WikiTemplate(name="foo", extra=WikiString(text="bar baz"))

        self.assertEqual(tag.as_text(), "")
        self.assertEqual(tag.as_wiki(), "{{ foo bar baz }}")

    def test_with_args(self):
        tag = WikiTemplate(
            name="foo",
            args=[WikiString(text="bar"), WikiString(text="baz")],
        )

        self.assertEqual(tag.as_text(), "")
        self.assertEqual(tag.as_wiki(), "{{ foo | bar | baz }}")

    def test_with_kwargs(self):
        tag = WikiTemplate(
            name="foo",
            kwargs={
                "bar": WikiString(text="1"),
                "baz": WikiString(text="qux"),
            },
        )

        self.assertEqual(tag.as_text(), "")
        self.assertEqual(tag.as_wiki(), "{{ foo | bar = 1 | baz = qux }}")

    def test_with_everything(self):
        tag = WikiTemplate(
            name="foo",
            args=[WikiString(text="bar"), WikiString(text="baz")],
            kwargs={
                "qux": WikiString(text="1"),
                "quux": WikiString(text="corge"),
            },
        )

        self.assertEqual(tag.as_text(), "")
        self.assertEqual(
            tag.as_wiki(), "{{ foo | bar | baz | qux = 1 | quux = corge }}"
        )


class TestWikiFlowEmpty:
    def test_as_text(self, wiki_empty_flow):
        assert_that(wiki_empty_flow.as_text()).is_equal_to("")

    def test_as_wiki(self, wiki_empty_flow):
        assert_that(wiki_empty_flow.as_wiki()).is_equal_to("")

    def test_as_html(self, wiki_empty_flow):
        assert_that(wiki_empty_flow.as_html()).is_equal_to("<span></span>")


class TestWikiFlow:
    def test_as_text(self, wiki_flow):
        assert_that(wiki_flow.as_text()).is_equal_to("italic text Example foo bar baz")

    def test_as_wiki(self, wiki_flow):
        assert_that(wiki_flow.as_wiki()).is_equal_to(
            "''italic text'' [[Example|https://example.com]] foo bar baz"
        )

    def test_as_html(self, wiki_flow):
        assert_that(wiki_flow.as_html()).is_equal_to(
            '<span><i>italic text</i> <a href="https://example.com">Example</a> foo bar baz</span>'
        )


class TestWikiListSimple:
    def test_as_text(self, wiki_list_simple):
        assert_that(wiki_list_simple.as_text()).is_equal_to(
            "1. one\n2. two\n3. three\n\n"
        )

    def test_as_wiki(self, wiki_list_simple):
        assert_that(wiki_list_simple.as_wiki()).is_equal_to("# one\n# two\n# three\n\n")

    def test_as_html(self, wiki_list_simple):
        assert_that(wiki_list_simple.as_html()).is_equal_to(
            "<ol>\n  <li>one</li>\n  <li>two</li>\n  <li>three</li>\n</ol>\n"
        )


class TestWikiListNested:
    def test_as_text(self, wiki_list_nested):
        assert_that(wiki_list_nested.as_text()).is_equal_to(
            textwrap.dedent(
                """\
                * one
                 ; definition term
                 : definition one
                 : definition two
                  1. two four one
                  2. two four two
                  3. two four three
                * three
                * four
                
                """
            )
        )

    def test_as_wiki(self, wiki_list_nested):
        assert_that(wiki_list_nested.as_wiki()).is_equal_to(
            textwrap.dedent(
                """\
                * one
                *; definition term
                *: definition one
                *: definition two
                **# two four one
                **# two four two
                **# two four three
                * three
                * four
                
                """
            )
        )

    def test_as_html(self, wiki_list_nested):
        assert_that(wiki_list_nested.as_html()).is_equal_to(
            textwrap.dedent(
                """\
                <ul>
                  <li>one</li>
                  <dl>
                    <dt>definition term</dt>
                    <dd>definition one</dd>
                    <dd>definition two</dd>
                    <ol>
                      <li>two four one</li>
                      <li>two four two</li>
                      <li>two four three</li>
                    </ol>
                  </dl>
                  <li>three</li>
                  <li>four</li>
                </ul>
                """
            )
        )


class TestWikiParagraph:
    def test_as_text(self, wiki_paragraph):
        assert_that(wiki_paragraph.as_text()).is_equal_to(
            textwrap.dedent(
                """\
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur placerat malesuada maximus.
                Nullam eleifend arcu commodo, sollicitudin neque non, ornare sapien. Vestibulum eros lacus, volutpat sit amet metus ut, varius imperdiet diam.
                1. one
                2. two
                3. three
                Ut ac augue sed metus cursus pretium id ut risus. Donec rhoncus dignissim metus in venenatis.
                
                """
            )
        )

    def test_as_wiki(self, wiki_paragraph):
        assert_that(wiki_paragraph.as_wiki()).is_equal_to(
            textwrap.dedent(
                """\
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur placerat malesuada maximus.
                Nullam eleifend arcu commodo, sollicitudin neque non, ornare sapien. Vestibulum eros lacus, volutpat sit amet metus ut, varius imperdiet diam.
                # one
                # two
                # three
                Ut ac augue sed metus cursus pretium id ut risus. Donec rhoncus dignissim metus in venenatis.
                
                """
            )
        )

    def test_as_html(self, wiki_paragraph):
        assert_that(wiki_paragraph.as_html()).is_equal_to(
            textwrap.dedent(
                """
                <p>
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur placerat malesuada maximus.<br/>
                  Nullam eleifend arcu commodo, sollicitudin neque non, ornare sapien. Vestibulum eros lacus, volutpat sit amet metus ut, varius imperdiet diam.<br/>
                  <ol>
                  <li>one</li>
                  <li>two</li>
                  <li>three</li>
                </ol>
                <br/>
                  Ut ac augue sed metus cursus pretium id ut risus. Donec rhoncus dignissim metus in venenatis.
                </p>
                """
            )
        )
