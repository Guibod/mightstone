from typing import Generator, Optional, Union

import pyparsing as pp

from mightstone.common import pydantic_model_recurse
from mightstone.services.wiki.models import (
    WikiElement,
    WikiFlow,
    WikiHtml,
    WikiLink,
    WikiList,
    WikiListBullet,
    WikiListItem,
    WikiPage,
    WikiParagraph,
    WikiString,
    WikiStyledText,
    WikiTemplate,
    WikiTitle,
)
from mightstone.services.wotc.models import RuleRef

HTML_START, HTML_END = pp.make_html_tags(pp.Word(pp.alphas).set_results_name("any_tag"))

# Suppressed
LBRACE = pp.Suppress("{{")
RBRACE = pp.Suppress("}}")
EQUALS = pp.Suppress("=")
PIPE = pp.Suppress("|")
LBRACKET = pp.Suppress("[[")
EOP = pp.Suppress(pp.OneOrMore(pp.LineStart() + pp.LineEnd()) | pp.StringEnd())
EOL = pp.Suppress(pp.LineEnd() | pp.StringEnd())
EMPTY_LINE = pp.Suppress(
    pp.LineStart() + pp.ZeroOrMore(" ") + pp.LineEnd()
).setWhitespaceChars("")

WIKI_STYLE_MARKER = (
    pp.Literal("'''''") | pp.Literal("'''") | pp.Literal("''")
).set_results_name("wiki_style_marker")

# Forwards
WIKI_HTML = pp.Forward()
WIKI_STYLED = pp.Forward()
WIKI_FLOW = pp.Forward()
WIKI_TEMPLATE = pp.Forward()
WIKI_LIST = pp.Forward()

WIKI_STRING = (
    pp.OneOrMore(
        pp.Char(pp.printables + " "),
        stop_on=pp.Literal("{{")
        | pp.Literal("[[")
        | HTML_START
        | HTML_END
        | WIKI_STYLE_MARKER
        | EOL,
    ).leave_whitespace()
).set_parse_action(lambda toks: WikiString(text=("".join(toks)).strip()))

WIKI_TITLE = (
    pp.Regex(
        r"(?P<level>={2,5})(\s+)?(?P<title>.+?)(\s+)?\1",
    )
    .set_results_name("wiki_title")
    .set_parse_action(
        lambda toks: WikiTitle(title=toks.title, level=len(toks.level) - 1)
    )
)
WIKI_LINK = (
    pp.Regex(
        r"\[\[(\s+)?(?P<target>[^\|]+?)((\s+)?\|(\s+)?(?P<displayed>.+?))?(\s+)?]]"
    )
    .set_results_name("wiki_link")
    .set_parse_action(
        lambda toks: WikiLink(
            url=toks.target.strip(), text=(toks.displayed or toks.target).strip()
        )
    )
)
WIKI_LIST_BULLET = (
    pp.OneOrMore(pp.Literal("*") | pp.Literal("#") | pp.Literal(":") | pp.Literal(";"))
    .set_results_name("wiki_list_token")
    .set_parse_action(lambda toks: WikiListBullet.from_string(toks.wiki_list_token))
)
WIKI_LIST_ITEM = (
    (WIKI_LIST_BULLET + WIKI_FLOW)
    .set_results_name("wiki_list_item")
    .set_parse_action(
        lambda toks: WikiListItem(
            content=toks.wiki_flow,
            level=toks.wiki_list_token.level,
            style=toks.wiki_list_token.style,
        )
    )
)
WIKI_PARAGRAPH = pp.Opt(EOL) + pp.Group(
    pp.OneOrMore(WIKI_LIST | (WIKI_FLOW + EOL), stop_on=EOP)
).set_parse_action(
    lambda toks: WikiParagraph.from_elements(*toks.wiki_paragraph)
).set_results_name(
    "wiki_paragraph"
)

WIKI_FLOW << pp.Opt(EOL) + pp.Group(
    pp.OneOrMore(
        WIKI_TEMPLATE | WIKI_LINK | WIKI_HTML | WIKI_STYLED | WIKI_STRING,
    )
).set_results_name("wiki_flow").set_parse_action(
    lambda toks: WikiFlow.from_elements(*toks.wiki_flow)
)

WIKI_HTML << (HTML_START + WIKI_FLOW + HTML_END).set_parse_action(
    lambda toks: WikiHtml.from_match(toks)
)

WIKI_STYLED << (
    pp.Combine(
        WIKI_STYLE_MARKER
        + pp.Opt(pp.White())
        + WIKI_FLOW
        + pp.Opt(pp.White())
        + pp.match_previous_literal(WIKI_STYLE_MARKER)
    )
    .set_results_name("wiki_styled")
    .set_parse_action(
        lambda toks: WikiStyledText.from_styled(
            toks.wiki_styled.wiki_flow,
            len(toks.wiki_styled.wiki_style_marker),
        )
    )
)

WIKI_LIST << (
    (pp.OneOrMore(WIKI_LIST_ITEM + EOL, stop_on=EMPTY_LINE))
    .set_name("wiki list")
    .set_results_name("wiki_list")
    .set_parse_action(lambda toks: WikiList.from_items(*toks.wiki_list))
)

TEMPLATE_STRING = pp.Combine(
    pp.OneOrMore(~LBRACE + ~RBRACE + ~PIPE + pp.CharsNotIn("\n", exact=1))
).set_parse_action(lambda toks: WikiString(text=("".join(toks)).strip()))

TEMPLATE_FLOW = pp.Opt(EOL) + pp.Group(
    pp.OneOrMore(
        WIKI_TEMPLATE | WIKI_LINK | WIKI_HTML | WIKI_STYLED | TEMPLATE_STRING,
    )
).set_results_name("wiki_flow").set_parse_action(
    lambda toks: WikiFlow.from_elements(*toks.wiki_flow)
)
PROPERTY_AS_KWARGS = (
    pp.Word(pp.alphanums + "_").set_results_name("keyword")
    + EQUALS
    + TEMPLATE_FLOW.set_results_name("value")
).set_results_name("kwargs", list_all_matches=True)
PROPERTY_AS_ARG = TEMPLATE_FLOW.set_results_name("args", list_all_matches=True)
PROPERTIES = pp.DelimitedList(PROPERTY_AS_KWARGS | PROPERTY_AS_ARG, delim=PIPE)
WIKI_TEMPLATE_NAME = pp.Word(pp.alphanums + "-_+").set_results_name("wiki_tag_name")
WIKI_TEMPLATE << pp.nested_expr(
    LBRACE,
    RBRACE,
    content=WIKI_TEMPLATE_NAME
    + pp.Optional(TEMPLATE_FLOW.set_results_name("extra"))
    + pp.Optional(PIPE + PROPERTIES)
    + pp.Optional(PIPE),
).set_results_name("wiki_template").set_name("wiki template").set_parse_action(
    lambda toks: WikiTemplate.from_item(toks.wiki_template[0])
)

PARSER = pp.ZeroOrMore(WIKI_TITLE | WIKI_PARAGRAPH).set_results_name("root")


class WikiParser:
    """
    A generic Wiki parser
    """

    def __init__(self, page: WikiPage, enable_packrat=True):
        self.page = page
        self.enable_packrat = enable_packrat

    @classmethod
    def flatten_results(
        cls,
        results: pp.ParseResults,
    ) -> Generator[WikiElement, None, None]:
        for result in results:
            if isinstance(result, str):
                continue

            if isinstance(result, WikiElement):
                yield result

            yield from cls.flatten_results(result)
        return

    def get_wiki_html(
        self, tags: Optional[list[str]] = None, max_matches=100, recurse=False
    ) -> Generator[WikiHtml, None, None]:
        """
        Extract all wiki HTML tags

        It is possible to limit result to a specific list of tags.
        If recurse option is activated, the method will instead resolve all nested
        tags.
        """
        if not self.page.source:
            return
        matches = WIKI_HTML.search_string(self.page.source, max_matches)

        def selector(x: WikiElement) -> bool:
            if tags:
                return isinstance(x, WikiHtml) and x.tag in tags

            return isinstance(x, WikiHtml)

        for match in matches:
            if recurse:
                yield from pydantic_model_recurse(match, selector)
            elif selector(match[0]):
                yield match[0]
        return

    def get_wiki_links(
        self, max_matches=100, recurse=False
    ) -> Generator[WikiLink, None, None]:
        """
        Extract all wiki links

        If recurse option is activated, the method will instead resolve all nested
        tags.
        """
        if not self.page.source:
            return
        matches = WIKI_LINK.search_string(self.page.source, max_matches)

        for match in matches:
            if recurse:
                yield from pydantic_model_recurse(match)
            else:
                yield match.wiki_link
        return

    def get_wiki_templates(
        self, templates: list[str], max_matches=100, recurse=False
    ) -> Generator[WikiTemplate, None, None]:
        """
        Extract all wiki templates (`{{template | foo | bar}}`) from a WikiPage at
        root level

        It is possible to filter results by template names.

        If recurse option is activated, the method will instead resolve all nested
        templates.
        """
        if not self.page.source:
            return
        matches = WIKI_TEMPLATE.search_string(self.page.source, max_matches)

        def selector(x: WikiElement) -> bool:
            if templates:
                return isinstance(x, WikiTemplate) and x.name in templates

            return isinstance(x, WikiTemplate)

        for match in matches:
            if recurse:
                yield from pydantic_model_recurse(match.wiki_template, selector)
            elif selector(match.wiki_template):
                yield match.wiki_template
        return

    def parse(self) -> Generator[WikiElement, None, None]:
        """
        Parse the wiki page and return a generator of WikiElements
        """
        parser = PARSER

        if not self.page.source:
            return

        parser.disable_memoization()
        if self.enable_packrat:
            parser.enable_packrat(True)

        for match, start, end in PARSER.scan_string(self.page.source):
            for item in match.root:
                yield item


class MtgWikiParser(WikiParser):
    """
    An Wiki syntax parser suitable for MTG Wiki needs
    """

    def get_infobox(self) -> Union[WikiTemplate, None]:
        """
        Get the infobox of the current page
        """
        iterator = self.get_wiki_templates(["Infobox"])
        return next(iterator, None)

    def get_stats(self) -> Generator[WikiTemplate, None, None]:
        """
        Get all stats template
        """
        found = False
        for tag in self.get_wiki_templates(templates=["stats"], recurse=True):
            found = True
            yield tag

        if not found:
            yield WikiTemplate(name="stats")

    def _extract_glossary_from_rule_tag(self, tag: WikiTemplate) -> Optional[str]:
        if tag.name == "CR+G":
            if not len(tag.args):
                return self.page.title
            return tag.get_arg_as_text(0)
        else:
            if "lookup" in tag.kwargs:
                return tag.get_kwarg_as_text("lookup")

            text = tag.get_arg_as_text(0)
            if len(tag.args) > 1:
                if text == "glossary":
                    return tag.get_arg_as_text(1)
            if text and not RuleRef.regex.match(text):
                # Not matching a rule regex, that’s a glossary
                return text
        return None

    def get_rules(self) -> Generator[Union[str, None], None, None]:
        """
        Extract all rule references from WikiPage
        """
        for tag in self.get_wiki_templates(["CR"], recurse=True):
            if not self._extract_glossary_from_rule_tag(tag):
                yield tag.get_arg_as_text(0)

    def get_glossaries(self) -> Generator[Optional[str], None, None]:
        """
        Extract all glossary references from WikiPage
        """
        for tag in self.get_wiki_templates(["CR+G", "CR"]):
            glossary = self._extract_glossary_from_rule_tag(tag)
            if glossary:
                yield glossary

    def get_cards(self) -> Generator[Optional[str], None, None]:
        """
        Extract all cards references from WikiPage
        """
        for tag in self.get_wiki_html(tags=["c"]):
            yield tag.content.as_text()

        for template in self.get_wiki_templates(templates=["Card"]):
            yield template.args[0].as_text()
