import logging
import urllib.parse
from typing import Generator, Union

from bs4 import BeautifulSoup, Tag
from pydantic_core._pydantic_core import ValidationError
from pyparsing import (
    CharsNotIn,
    Combine,
    Forward,
    OneOrMore,
    Optional,
    ParseResults,
    Suppress,
    Word,
    alphanums,
    alphas,
    delimited_list,
    nested_expr,
)

from mightstone.ass import synchronize
from mightstone.rule.models.ability import Ability, AbilityList, AbilityType
from mightstone.services import MightstoneHttpClient

from ...rule.models.color import Identity, IdentityMap
from .models import WikiString, WikiTag


class Wiki(MightstoneHttpClient):
    """
    Scryfall API client
    """

    base_url = "https://mtg.fandom.com"

    async def export_pages_async(self, pages: list[str]):
        response = await self.client.post(
            "/wiki/Special:Export",
            data={
                "catname": "",
                "pages": "\n".join(pages),
                "curonly": "1",
                "wpDownload": 1,
                "wpEditToken": "+\\",
                "title": "Special:Export",
            },
        )
        return response.content

    export_pages = synchronize(export_pages_async)

    async def export_category_async(self, category) -> bytes:
        response = await self.client.post(
            "/wiki/Special:Export",
            data={
                "addcat": "Add",
                "catname": category,
                "pages": "",
                "curonly": "1",
                "wpDownload": 1,
                "wpEditToken": "+\\",
                "title": "Special:Export",
            },
        )
        soup = BeautifulSoup(response.content, "lxml")
        pages_as_source = soup.find("textarea", {"name": "pages"})
        if not isinstance(pages_as_source, Tag):
            raise RuntimeError("Unable to resolve pages for category %s" % category)
        pages = [page.strip() for page in pages_as_source.decode_contents().split("\n")]
        return await self.export_pages_async(pages)

    export_category = synchronize(export_category_async)

    async def all_pages(self):
        raise NotImplementedError()

    async def scrape_abilities_async(self) -> AbilityList:
        from ...rule.data.color import identities

        categories = [
            "Keywords/Static",
            "Keywords/Activated",
            "Keywords/Characteristic-defining",
            "Keywords/Evasion",
            "Keywords/Spell",
            "Keywords/Triggered",
        ]

        list = AbilityList()
        for category in categories:
            export = await self.export_category_async(category)
            adapter = WikiAbilityAdapter(self.base_url, export, identities=identities)
            for ability in adapter.abilities():
                list.abilities.append(ability)
        return list

    scrape_abilities = synchronize(scrape_abilities_async)


class WikiParser:
    LBRACE = Suppress("{{")
    RBRACE = Suppress("}}")
    EQUALS = Suppress("=")
    PIPE = Suppress("|")

    WIKI_TAG = Forward()
    STRING_SEQUENCE = Combine(
        OneOrMore(~LBRACE + ~RBRACE + ~PIPE + CharsNotIn("\n", exact=1))
    )
    TEMPLATE_STRING = OneOrMore(WIKI_TAG | STRING_SEQUENCE)
    PROPERTY_NAME = Word(alphanums + "_")
    WIKI_BLOCK_NAME = Word(alphas + alphanums + "-_+").set_results_name("wiki_tag_name")

    PROPERTY_AS_KWARGS = (PROPERTY_NAME + EQUALS + TEMPLATE_STRING).set_results_name(
        "kwargs", list_all_matches=True
    )
    PROPERTY_AS_ARG = TEMPLATE_STRING.set_results_name("args", list_all_matches=True)
    PROPERTY = PROPERTY_AS_KWARGS | PROPERTY_AS_ARG
    PROPERTIES = delimited_list(PROPERTY, delim=PIPE)

    WIKI_TAG << nested_expr(
        LBRACE,
        RBRACE,
        content=WIKI_BLOCK_NAME
        + Optional(TEMPLATE_STRING.set_results_name("extra"))
        + Optional(PIPE + PROPERTIES)
        + Optional(PIPE),
    ).set_results_name("wiki_tag")

    def __init__(self, name, content):
        self.name = name
        self.content = content

    @classmethod
    def flatten_results(
        cls,
        results: ParseResults,
    ) -> Generator[ParseResults, None, None]:
        for result in results:
            if isinstance(result, str):
                continue

            if result.wiki_tag_name:
                yield result

            yield from cls.flatten_results(result)
        return

    def get_infobox(self) -> Union[WikiTag, None]:
        iterator = self.get_wiki_tags(["Infobox"])
        return next(iterator, None)

    def get_stats(self) -> Generator[WikiTag, None, None]:
        found = False
        for tag in self.get_wiki_tags(["stats"], recurse=True):
            found = True
            yield tag

        if not found:
            yield WikiTag(tag="stats")

    def extract_glossary_from_rule(self, tag: WikiTag) -> Union[WikiTag, str, None]:
        if tag.tag == "CR+G":
            if not len(tag.args):
                return self.name
            return tag.args[0].tokens[0]
        else:
            if "lookup" in tag.kwargs:
                return tag.kwargs["lookup"].tokens[0]
            if len(tag.args) > 1 and tag.args[0].tokens[0] == "glossary":
                return tag.args[1].tokens[0]
        return None

    def get_rules(self) -> Generator[Union[str, WikiTag], None, None]:
        for tag in self.get_wiki_tags(["CR"]):
            if not self.extract_glossary_from_rule(tag):
                yield tag.args[0].tokens[0]

    def get_glossaries(self) -> Generator[Union[str, WikiTag], None, None]:
        for tag in self.get_wiki_tags(["CR+G", "CR"]):
            glossary = self.extract_glossary_from_rule(tag)
            if glossary:
                yield glossary

    def get_wiki_tags(
        self, tags: list[str], max_matches=100, recurse=False
    ) -> Generator[WikiTag, None, None]:
        matches = self.WIKI_TAG.search_string(self.content, max_matches)

        if recurse:
            iterator = self.flatten_results(matches)
        else:
            iterator = [tag for match in matches for tag in match.wiki_tag]  # type: ignore

        for tag in iterator:
            if tag.wiki_tag_name in tags:
                yield self.build_wiki_tag(tag)
        return

    def build_wiki_string(self, tokens: list[Union[ParseResults, str]]) -> WikiString:
        out = WikiString()
        for token in tokens:
            if isinstance(token, str):
                out.tokens.append(token.strip())
            else:
                out.tokens.append(self.build_wiki_tag(token))
        return out

    def build_wiki_tag(self, wiki_tag: ParseResults) -> WikiTag:
        args = []
        if wiki_tag.args:
            args = [self.build_wiki_string(arg) for arg in wiki_tag.args]

        kwargs = {}
        if wiki_tag.kwargs:
            for x in wiki_tag.kwargs:
                kwargs[x[0].strip()] = self.build_wiki_string(x[1:])

        extra = None
        if wiki_tag.extra:
            extra = self.build_wiki_string(wiki_tag.extra)

        return WikiTag(
            tag=wiki_tag.wiki_tag_name, args=args, kwargs=kwargs, extra=extra
        )


class WikiAbilityAdapter:
    def __init__(self, base_url: str, content: bytes, identities: IdentityMap):
        self.base_url = base_url
        self.soup = BeautifulSoup(content, "lxml")
        self.identities = identities

    def pages(self) -> list[Tag]:
        return self.soup.find_all("page") or []

    @staticmethod
    def map_ability_types(infobox: WikiTag) -> list[AbilityType]:
        types: list[str] = [
            infobox.get_kwarg([key]) or ""
            for key in sorted(infobox.kwargs.keys())
            if key.startswith("type")
        ]

        out = []
        for t in types:
            try:
                out.append(AbilityType(t.lower()))
            except ValueError:
                ...
        return out

    def abilities(self) -> Generator[Ability, None, None]:
        for page in self.pages():
            title_as_str = page.find_next("title").text  # type: ignore
            parser = WikiParser(
                title_as_str,
                page.find_next("text").text,  # type: ignore
            )
            url = f"{self.base_url}/wiki/{urllib.parse.quote(title_as_str)}"

            infobox = parser.get_infobox()
            if not infobox:
                logging.warning("Unable to parse %s, no infobox found" % (url))
                continue
            rules = list(parser.get_rules())
            stats = list(parser.get_stats())

            for stat in stats:
                try:
                    yield Ability.model_validate(
                        {
                            "name": stat.get_arg(0) or title_as_str,
                            "types": self.map_ability_types(infobox),
                            "rules": rules,
                            "wiki": url,
                            "introduced": infobox.get_kwarg(["first"]),
                            "last_seen": infobox.get_kwarg(["last"]),
                            "has_cost": bool(infobox.get_kwarg(["cost", "N"])),
                            "reminder": infobox.get_kwarg(["reminder"]),
                            "stats": self.map_stats(stat),
                            "storm": infobox.get_kwarg(["storm"]),
                        }
                    )
                except ValidationError as e:
                    logging.warning(
                        "%s (%s) failed to be validated: %s"
                        % (url, stat.get_arg(0) or title_as_str, e)
                    )
                    continue

    def map_stats(self, tag: WikiTag) -> dict[str, int]:
        out = {}
        for k, v in tag.kwargs.items():
            try:
                identity = self.identities[k.lower()]
                out[identity.canonical] = int(v.tokens[0])   # type: ignore
            except KeyError:
                ...

        return out
