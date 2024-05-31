import asyncio
import logging
import re
from datetime import date, timedelta
from io import StringIO
from typing import List, Optional

from mightstone.ass import synchronize
from mightstone.services import MightstoneHttpClient
from mightstone.services.wotc.models import ComprehensiveRules

logger = logging.getLogger("mightstone")


class RuleExplorer(MightstoneHttpClient):
    base_url = "https://media.wizards.com"

    async def open_async(self, path: Optional[str] = None) -> ComprehensiveRules:
        """
        Open a local or remote comprehensive rule document, if no path is provided
        then the latest rules from Wizards of the Coast website is pulled.

        :param path: A local path, or an URL to the rule document
        :return: A ``ComprehensiveRules`` instance
        """
        if not path:
            path = await self.latest_async()

        if path.startswith("http"):
            f = await self.client.get(path)
            f.raise_for_status()
            try:
                content = StringIO(f.content.decode("UTF-8"))
            except UnicodeDecodeError:
                content = StringIO(f.content.decode("iso-8859-1"))

            return ComprehensiveRules.parse(content)

        with open(path, "r") as f:
            return ComprehensiveRules.parse(f)

    open = synchronize(open_async)

    async def latest_async(self) -> str:
        """
        Resolves wizard latest published ruleset

        :return: The url of the latest ruleset to date
        """
        pattern = re.compile(re.escape(self.base_url) + r"/.*/MagicComp.+\.txt")

        f = await self.client.get("https://magic.wizards.com/en/rules")
        f.raise_for_status()
        res = pattern.search(f.text)
        if res:
            return res.group(0).replace(" ", "%20")
        raise RuntimeError("Unable to find URL of the last comprehensive rules")

    latest = synchronize(latest_async)

    async def explore_async(
        self, after: date, before: Optional[date] = None, concurrency=3
    ) -> List[str]:
        """
        Explore the wizards of the coast website to find any rule between two timestamp.

        Wizards don’t support an historic index of previous rules, this method tries to
        compensate by providing a brute force attempt to pull magic rule history.
        This method will brute force every possible rule using the current format:

        https://media.wizards.com/YYYY/downloads/MagicComp%20Rules%20{YYYY}{MM}{DD}.txt

        :param after: The min date to scan
        :param before: The max date to scan (defaults to today)
        :param concurrency: The max number of concurrent HTTP requests
        :return: A list of existing rules url
        """
        if not before:
            before = date.today()

        urls = []
        for n in range(int((before - after).days)):
            d = after + timedelta(n)
            urls.append(d.strftime("/%Y/downloads/MagicComp%%20Rules%%20%Y%m%d.txt"))
            urls.append(d.strftime("/%Y/downloads/MagicCompRules%%20%Y%m%d.txt"))

        found = []
        sem = asyncio.Semaphore(concurrency)

        async def test_url(url: str):
            async with sem:
                logger.debug("GET %s", url)
                resp = await self.client.get(url)
                if resp.is_success:
                    logger.info("Found %s", url)
                    found.append(url)

        tasks = []
        for url in urls:
            task = asyncio.ensure_future(test_url(url))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)

        return found

    explore = synchronize(explore_async)
