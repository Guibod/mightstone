import logging
from typing import AsyncGenerator, Generator, Optional, Union

from bs4 import BeautifulSoup, Tag
from pydantic_core import ValidationError

from mightstone.ass import synchronize
from mightstone.rule.models.ability import Ability, AbilityList, AbilityType
from mightstone.services import MightstoneHttpClient

from .models import WikiPage, WikiTemplate
from .parser import MtgWikiParser

# TODO: Consolidate affinities/primary/secondary


class Wiki(MightstoneHttpClient):
    """
    Scryfall API client
    """

    base_url = "https://mtg.fandom.com"

    async def export_pages_async(self, pages: list[str]) -> bytes:
        """
        Requests wiki on `Special:Export` page for a given set of pages

        Returns the raw output from the export
        """
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
        response.raise_for_status()
        return response.content

    export_pages = synchronize(export_pages_async)

    async def export_category_async(self, category) -> bytes:
        """
        Requests wiki on `Special:Export` page for a given category

        Returns the raw output from the export
        """
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
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        pages_as_source = soup.find("textarea", {"name": "pages"})
        if not isinstance(pages_as_source, Tag):
            raise RuntimeError("Unable to resolve pages for category %s" % category)
        pages = [page.strip() for page in pages_as_source.decode_contents().split("\n")]
        return await self.export_pages_async(pages)

    export_category = synchronize(export_category_async)

    async def explore_pages(self, redirect=False) -> AsyncGenerator[str, None]:
        """
        Explore the `Special:AllPages` pages to generate a full list of available pages

        You can optionally request pages that are redirects to others.
        """
        if redirect:
            selector = ".mw-allpages-chunk li a"
        else:
            selector = ".mw-allpages-chunk li a:not(.mw-redirect)"
        selector_next = ".mw-allpages-nav a"
        next_page: Optional[str] = "/wiki/Special:AllPages"

        while next_page:
            response = await self.client.get(next_page)
            soup = BeautifulSoup(response.content, "lxml")

            for tag in soup.select(selector):
                yield tag.text

            next_page = next(
                (
                    tag["href"]  # type: ignore
                    for tag in soup.select(selector_next)
                    if "Next page" in tag.text
                ),
                None,
            )

        return

    async def scrape_abilities_async(self) -> AbilityList:
        """
        Build an AbilityList object from the content of all `Keywords` categories

        This is used to build `mightstone.rule.data.ability` content
        """

        categories = [
            "Keywords/Static",
            "Keywords/Activated",
            "Keywords/Characteristic-defining",
            "Keywords/Evasion",
            "Keywords/Spell",
            "Keywords/Triggered",
        ]

        out = AbilityList()
        for category in categories:
            export = await self.export_category_async(category)
            adapter = WikiExportParser(self.base_url, export)

            for ability in adapter.abilities():
                out.abilities.append(ability)
        return out

    scrape_abilities = synchronize(scrape_abilities_async)


class WikiExportParser:
    """
    Raw page parser
    """

    def __init__(self, base_url: str, content: bytes):
        self.base_url = base_url
        self.soup = BeautifulSoup(content, "lxml")

    def page(self, name) -> Union[WikiPage, None]:
        """
        Tries to recover a named page (case sensitive) from the export
        Returns None if not available
        """
        for page in self.pages():
            if page.title == name:
                return page
        return None

    def pages(self) -> Generator[WikiPage, None, None]:
        """
        A generator that extract all WikiPage from a Wiki dump
        """
        for page in self.soup.find_all("page"):
            yield WikiPage.from_tag(page, self.base_url)

    def abilities(self) -> Generator[Ability, None, None]:
        """
        A generator that extract all Abilities from a Wiki dump
        """
        for page in self.pages():
            page_adapter = WikiPageAdapter(page)

            try:
                for ability in page_adapter.abilities():
                    yield ability
            except ValueError:
                ...


class WikiPageAdapter:
    def __init__(self, page: WikiPage):
        self.page = page

    @staticmethod
    def map_ability_types(infobox: WikiTemplate) -> list[AbilityType]:
        types: list[Union[str, None]] = [
            infobox.get_kwarg_as_text(key)
            for key in sorted(infobox.kwargs.keys())
            if key.startswith("type")
        ]

        out = []
        for t in types:
            try:
                if t:
                    out.append(AbilityType(t.lower()))
            except (ValueError, AttributeError):
                ...
        return out

    def abilities(self) -> Generator[Ability, None, None]:
        parser = MtgWikiParser(self.page)

        infobox = parser.get_infobox()
        if not infobox:
            raise ValueError("Unable to parse %s, no infobox found" % self.page.url)

        rules = list(parser.get_rules())
        glossaries = list(parser.get_glossaries())
        stats = list(parser.get_stats())

        for stat in stats:
            try:
                yield Ability.model_validate(
                    {
                        "name": stat.get_arg_as_text(0) or self.page.title,
                        "types": self.map_ability_types(infobox),
                        "rules": rules,
                        "glossaries": glossaries,
                        "wiki": self.page.url,
                        "introduced": infobox.get_kwarg_as_text("first"),
                        "last_seen": infobox.get_kwarg_as_text("last"),
                        "has_cost": bool(infobox.get_kwarg_as_text("cost", "N")),
                        "reminder": infobox.get_kwarg_as_text("reminder"),
                        "stats": self.map_stats(stat),
                        "storm": infobox.get_kwarg_as_text("storm"),
                    }
                )
            except ValidationError as e:
                logging.warning(
                    "%s (%s) failed to be validated: %s"
                    % (self.page.url, stat.get_arg(0) or self.page.title, e)
                )
                continue

    @staticmethod
    def map_stats(tag: WikiTemplate) -> dict[str, int]:
        out = {}
        for k, v in tag.kwargs.items():
            try:
                out[k.lower()] = int(v.text)  # type: ignore
            except ValueError:
                ...

        return out
