import html
import urllib.parse
from abc import abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from bs4 import NavigableString, Tag
from pydantic_core import Url
from pyparsing import ParseResults

from mightstone.core import (
    MightstoneDocument,
    MightstoneModel,
    MightstoneSerializableDocument,
)


def _find_nested_bs4_tag(
    tag: Union[Tag, NavigableString, None], keys: list[str], fallback=None
):
    try:
        while True:
            if not isinstance(tag, Tag):
                return None

            k = keys.pop(0)
            tag = tag.find(k)
    except IndexError:
        try:
            return tag.text  # type: ignore
        except AttributeError:
            return fallback


class WikiTextStyle(Enum):
    NONE = 0
    ITALIC = 1
    BOLD = 2
    ITALIC_BOLD = 3


class WikiListStyle(Enum):
    BULLET = 0
    NUMBERED = 1
    DEF = 2


class WikiListItemStyle(str, Enum):
    BULLET = "*"
    NUMBERED = "#"
    TERM = ";"
    DEFINITION = ":"

    def __str__(self) -> str:
        return self.value


class WikiElement(MightstoneModel):
    def __str__(self):
        return self.as_text()

    @abstractmethod
    def as_text(self) -> str:
        pass

    @abstractmethod
    def as_html(self) -> str:
        pass

    @abstractmethod
    def as_wiki(self) -> str:
        pass


class WikiString(WikiElement):
    """
    Representation of a string in the wiki
    """

    text: str = ""

    def as_text(self):
        return self.text

    def as_wiki(self):
        return self.text

    def as_html(self) -> str:
        return self.text


class WikiStyledText(WikiElement):
    """
    Representation of a styled text content
    """

    content: WikiElement
    style: WikiTextStyle = WikiTextStyle.NONE

    @property
    def wiki_marker(self) -> str:
        if self.style == WikiTextStyle.ITALIC_BOLD:
            return "'''''"
        elif self.style == WikiTextStyle.BOLD:
            return "'''"
        elif self.style == WikiTextStyle.ITALIC:
            return "''"
        else:
            return ""

    def as_text(self) -> str:
        return self.content.as_text()

    def as_wiki(self) -> str:
        if self.style == WikiTextStyle.ITALIC_BOLD:
            marker = "'''''"
        elif self.style == WikiTextStyle.BOLD:
            marker = "'''"
        elif self.style == WikiTextStyle.ITALIC:
            marker = "''"
        else:
            marker = ""

        return marker + self.content.as_text() + marker

    def as_html(self) -> str:
        if self.style == WikiTextStyle.ITALIC_BOLD:
            tag = (
                "<b><i>",
                "</i></b>",
            )
        elif self.style == WikiTextStyle.BOLD:
            tag = "<b>", "</b>"
        elif self.style == WikiTextStyle.ITALIC:
            tag = "<i>", "</i>"
        else:
            tag = "", ""

        return tag[0] + self.content.as_text() + tag[1]
        return self.content.as_text()

    @staticmethod
    def from_styled(content: str, quotes_count: int):
        style = WikiTextStyle.NONE
        if quotes_count == 2:
            style = WikiTextStyle.ITALIC
        elif quotes_count == 3:
            style = WikiTextStyle.BOLD
        elif quotes_count == 5:
            style = WikiTextStyle.ITALIC_BOLD

        if isinstance(content, str):
            return WikiStyledText(content=WikiString(text=content), style=style)
        else:
            return WikiStyledText(content=content, style=style)


class WikiLink(WikiElement):
    """
    Representation of a WikiLink
    """

    text: str
    url: str

    def as_text(self) -> str:
        return self.text

    def as_wiki(self) -> str:
        if self.text == self.url:
            return f"[[{self.url}]]"
        else:
            return f"[[{self.text}|{self.url}]]"

    def as_html(self) -> str:
        return f'<a href="{html.escape(self.url)}">{html.escape(self.text)}</a>'


class WikiRevision(MightstoneModel):
    """
    A Revision description in the Wiki dump

    This object contains the source of the page on a given timestamp
    """

    id: int
    parent_id: int
    timestamp: datetime
    contributor_name: Optional[str]
    contributor_id: Optional[int]
    origin: int
    source: str

    @staticmethod
    def from_tag(revision: Tag):
        return WikiRevision(
            id=_find_nested_bs4_tag(revision, ["id"]),
            parent_id=_find_nested_bs4_tag(revision, ["parentid"]),
            source=html.unescape(_find_nested_bs4_tag(revision, ["text"])),
            timestamp=_find_nested_bs4_tag(revision, ["timestamp"]),
            contributor_name=_find_nested_bs4_tag(
                revision, ["contributor", "username"]
            ),
            contributor_id=_find_nested_bs4_tag(revision, ["contributor", "id"]),
            origin=_find_nested_bs4_tag(revision, ["origin"]),
        )


class WikiPage(MightstoneDocument):
    """
    A wiki dump page
    """

    id: int
    title: str
    revisions: list[WikiRevision]
    url: Url

    @property
    def source(self) -> Union[str, None]:
        try:
            return self.revisions[0].source
        except IndexError:
            return None

    @staticmethod
    def from_tag(page: Tag, base_url: str):
        title = _find_nested_bs4_tag(page, ["title"])
        return WikiPage(
            id=_find_nested_bs4_tag(page, ["id"]),
            title=title,
            url=Url(f"{base_url}/wiki/{urllib.parse.quote(title)}"),
            revisions=[
                WikiRevision.from_tag(revision)
                for revision in page.find_all("revision")
            ],
        )


class SerializableWikiPage(WikiPage, MightstoneSerializableDocument):
    id: int  # type: ignore


class WikiTemplate(WikiElement):
    """
    Representation of a wiki template

    A template is wrapped in double curled brace: {{1}}, {{stats | uw=10}}
    """

    name: str
    extra: Optional[WikiElement] = None
    kwargs: dict[str, WikiElement] = {}
    args: list[WikiElement] = []

    def get_kwarg(self, *keys: str) -> Union[WikiElement, None]:
        for key in keys:
            if key in self.kwargs:
                return self.kwargs[key]

        return None

    def get_kwarg_as_text(self, *keys: str) -> Union[str, None]:
        try:
            return self.get_kwarg(*keys).as_text()  # type: ignore
        except AttributeError:
            return None

    def get_arg(self, index: int) -> Union[WikiElement, None]:
        try:
            return self.args[index]
        except IndexError:
            return None

    def get_arg_as_text(self, index: int) -> Union[str, None]:
        try:
            return self.get_arg(index).as_text()  # type: ignore
        except AttributeError:
            return None

    def as_text(self):
        return ""

    def as_html(self):
        return ""

    def as_wiki(self):
        parts = [self.name]
        if self.extra:
            parts = [f"{self.name} {self.extra}"]

        if self.args:
            parts.append(" | ".join(map(str, self.args)))

        if self.kwargs:
            parts.append(
                " | ".join(map(lambda kv: f"{kv[0]} = {kv[1]}", self.kwargs.items()))
            )

        return "{{ " + " | ".join(parts) + " }}"

    @staticmethod
    def from_item(wiki_tag: ParseResults) -> "WikiTemplate":
        args = []
        if wiki_tag.args:
            args = [arg[0] for arg in wiki_tag.args]

        kwargs = {}
        if wiki_tag.kwargs:
            for x in wiki_tag.kwargs:
                kwargs[x[0].strip()] = x[1]

        extra = None
        if wiki_tag.extra:
            extra = wiki_tag.extra[0]

        return WikiTemplate(
            name=wiki_tag.wiki_tag_name, args=args, kwargs=kwargs, extra=extra
        )


class WikiFlow(WikiElement):
    """
    A representation of a wiki flow

    A wiki flow is a succession of other wiki element that are displayed inline such
    as links, styled text, templates...
    """

    items: list[Union[WikiElement]] = []

    def as_text(self):
        return " ".join([token.as_text() for token in self.items])

    def as_wiki(self):
        return " ".join([token.as_wiki() for token in self.items])

    def as_html(self):
        return (
            "<span>" + " ".join([token.as_html() for token in self.items]) + "</span>"
        )

    @staticmethod
    def from_elements(*elements: Union[str, WikiElement]):
        tokens = []
        if len(elements) == 1:
            return elements[0]

        for element in elements:
            if isinstance(element, str):
                element = WikiString(text=element)
            tokens.append(element)

        return WikiFlow(items=tokens)


class WikiParagraph(WikiElement):
    """
    Representation of a wiki paragraph

    A wiki paragraph is separated by a blank line
    """

    items: list[Union[WikiElement]] = []

    def as_text(self):
        out = ""
        for item in self.items:
            out += item.as_text()
            if not isinstance(item, WikiList):
                out += "\n"
            else:
                out = out[:-1]
        return out + "\n"

    def as_wiki(self):
        out = ""
        for item in self.items:
            out += item.as_wiki()
            if not isinstance(item, WikiList):
                out += "\n"
            else:
                out = out[:-1]
        return out + "\n"

    def as_html(self):
        return (
            "\n<p>\n"
            + "<br/>\n".join(["  " + token.as_html() for token in self.items])
            + "\n"
            + "</p>\n"
        )

    @staticmethod
    def from_elements(*elements: WikiElement):
        tokens = []

        for element in elements:
            tokens.append(element)

        return WikiParagraph(items=tokens)


class WikiTitle(WikiElement):
    """
    Representation of a wiki title

    For instance: ==Level 1==, ====Level 3====
    """

    title: str
    level: int = 1

    def as_text(self):
        return self.title

    def as_html(self):
        return f"\n<h{self.level}>{self.title}</h{self.level}>"

    def as_wiki(self):
        markup = "=" * (self.level + 1)
        return f"\n\n{markup} {self.title} {markup}\n"


class WikiListBullet(MightstoneModel):
    level: int = 0
    style: WikiListItemStyle = WikiListItemStyle.BULLET

    @staticmethod
    def from_string(string: str):
        style = WikiListItemStyle(string[-1])
        return WikiListBullet(level=len(string) - 1, style=style)


class WikiListItem(WikiElement):
    """
    Representation of a list item

    For instance: ** Item
    """

    level: int = 0
    style: WikiListItemStyle = WikiListItemStyle.BULLET
    content: WikiElement

    def as_text(self):
        return f"{self.style} {self.content.as_text()}"

    def as_wiki(self):
        return f"{self.style} {self.content.as_text()}"

    def as_html(self):
        if self.style == WikiListItemStyle.DEFINITION:
            tag = "<dd>", "</dd>"
        elif self.style == WikiListItemStyle.TERM:
            tag = "<dt>", "</dt>"
        else:
            tag = "<li>", "</li>"
        return f"{tag[0]}{self.content.as_html()}{tag[1]}"


class WikiList(WikiElement):
    """
    Representation of a Wiki List
    """

    level: int = 0
    items: list[Union[WikiListItem, "WikiList"]] = []
    style: WikiListStyle = WikiListStyle.BULLET

    @staticmethod
    def from_items(*items: WikiListItem):
        style = WikiListStyle.BULLET
        if items[0].style == WikiListItemStyle.NUMBERED:
            style = WikiListStyle.NUMBERED
        elif items[0].style in (WikiListItemStyle.TERM, WikiListItemStyle.DEFINITION):
            style = WikiListStyle.DEF

        the_list = WikiList(level=items[0].level, style=style)
        iterator = iter([*items])

        while (item := next(iterator, None)) is not None:
            if item.level > the_list.level:
                nested = [item]
                while (
                    item := next(iterator, None)
                ) is not None and item.level > the_list.level:
                    nested.append(item)

                the_list.items.append(the_list.from_items(*nested))
            if item:
                the_list.items.append(item)
        return the_list

    def as_text(self):
        indent = " " * self.level
        out = ""
        for i, item in enumerate(self.items, 1):
            if isinstance(item, WikiList):
                out += item.as_text()
            elif self.style == WikiListStyle.NUMBERED:
                out += f"{indent}{item.as_text()}\n".replace("#", f"{i}.")
            else:
                out += f"{indent}{item.as_text()}\n"
        if self.level == 0:
            out += "\n"
        return out

    def as_wiki(self):
        indent = "*" * self.level
        out = ""
        for item in self.items:
            if isinstance(item, WikiList):
                out += item.as_wiki()
            else:
                out += f"{indent}{item.as_wiki()}\n"
        if self.level == 0:
            out += "\n"
        return out

    def as_html(self):
        if self.style == WikiListStyle.DEF:
            tag = "<dl>", "</dl>"
        elif self.style == WikiListStyle.NUMBERED:
            tag = "<ol>", "</ol>"
        else:
            tag = "<ul>", "</ul>"

        indent = "  " * self.level
        out = f"{indent}{tag[0]}\n"
        for item in self.items:
            if isinstance(item, WikiList):
                out += item.as_html()
            else:
                out += f"{indent}  {item.as_html()}\n"
        out += f"{indent}{tag[1]}\n"
        return out


class WikiHtml(WikiElement):
    """
    Representation of an HTML tag

    For instance: <c></c>
    """

    tag: str
    attributes: dict[str, str] = {}
    content: WikiElement

    @staticmethod
    def from_match(toks: ParseResults):
        return WikiHtml(
            tag=toks.tag,
            content=toks.wiki_flow,
            attributes={
                k: v
                for k, v in toks["startW(A-Za-Z)"].items()
                if k
                not in [
                    "tag",
                    "empty",
                ]
            },
        )

    @property
    def opening_tag(self) -> str:
        attributes = ""
        if len(self.attributes):
            attributes = " " + " ".join(
                [
                    f'{html.escape(k)}="{html.escape(v)}"'
                    for k, v in self.attributes.items()
                ]
            )
        return f"<{html.escape(self.tag)}{attributes}>"

    @property
    def closing_tag(self) -> str:
        return f"</{html.escape(self.tag)}>"

    def as_text(self):
        return self.content.as_text()

    def as_wiki(self):
        return self.opening_tag + self.content.as_wiki() + self.closing_tag

    def as_html(self):
        return self.opening_tag + self.content.as_html() + self.closing_tag
