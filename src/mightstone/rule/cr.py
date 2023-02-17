import asyncio
import logging
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from io import StringIO
from itertools import takewhile
from typing import Dict, List, Mapping, TextIO

import aiohttp
import requests

from mightstone.core import MightstoneModel

# TODO: get rid of requests dependency, use async client


logger = logging.getLogger(__name__)


class RuleRef(str):
    """
    Rules reference use the same pattern with a rule number

    <rule>[.<sub_rule>[<letter>]][<trailing_dot>]

     * rule: an integer of three digit, first digit matches parent section
     * sub_rule: an integer
     * letter: a letter (o, and l are not valid)
     * trailing dot: used in table of content for readability purpose
       and then used inconsistently in the rule themselves.

    RuleRef consider the trailing dot a legal, but won’t keep it in its canonical
    notation
    """

    regex = re.compile(
        r"(?P<reference>"
        r"(?P<rule>\d{3})"
        r"(\.((?P<sub_rule>\d+)(?P<letter>[a-z])?))?"
        r"(?P<trailing_dot>\.)?"
        r")"
    )

    def __new__(cls, value, *args, **kwargs):
        return super(RuleRef, cls).__new__(cls, value)

    def __init__(self, value):
        res = self.regex.match(value)
        if not res:
            raise ValueError(f"{self} is not a valid reference")
        if res.group("letter") in ["l", "o"]:
            raise ValueError(
                f"{self} is not a valid reference, letters (o, l) are invalid"
            )

        self.rule = int(res.group("rule"))
        self.sub_rule = None
        if res.group("sub_rule"):
            self.sub_rule = int(res.group("sub_rule"))
        self.letter = res.group("letter")
        self.canonical = self.build(self.rule, self.sub_rule, self.letter)
        self.section = int(res.group("rule")[0])

    @classmethod
    def build(cls, rule: int, sub_rule: int = None, letter: str = None):
        out = str(rule)
        if sub_rule:
            out += f".{sub_rule}"
            if letter:
                out += f"{letter}"
        return out

    def next(self):
        if self.letter and self.sub_rule and self.rule:
            increment = 1
            if self.letter in ["k", "n"]:
                increment = 2
            return RuleRef(
                self.build(self.rule, self.sub_rule, chr(ord(self.letter) + increment))
            )

        if self.sub_rule and self.rule:
            return RuleRef(self.build(self.rule, self.sub_rule + 1))

        return RuleRef(self.build(self.rule + 1))

    def prev(self):
        if self.letter == "a":
            return None
        if self.sub_rule == 1 and not self.letter:
            return None
        if self.rule == 100 and not self.sub_rule:
            return None

        if self.letter and self.sub_rule and self.rule:
            increment = 1
            if self.letter in ["m", "p"]:
                increment = 2

            return RuleRef(
                self.build(self.rule, self.sub_rule, chr(ord(self.letter) - increment))
            )

        if self.sub_rule and self.rule:
            return RuleRef(self.build(self.rule, self.sub_rule - 1))

        return RuleRef(self.build(self.rule - 1))

    def __eq__(self, other):
        try:
            return self.canonical == other.canonical
        except AttributeError:
            return self.canonical == other


class SectionRef(str):
    regex = re.compile(r"(?P<reference>(?P<section>\d)\.?)")

    def __new__(cls, value, *args, **kwargs):
        return super(SectionRef, cls).__new__(cls, value)

    def __init__(self, value):
        res = self.regex.match(value)
        if not res:
            raise ValueError(f"{self} is not a valid reference")
        self.section = int(res.group("section"))


class RuleText(str):
    """
    A string than can contain reference to rule
    """

    see_rule = re.compile(r"rule " + RuleRef.regex.pattern)
    see_section = re.compile(r"section " + SectionRef.regex.pattern)

    def __new__(cls, value, *args, **kwargs):
        return super(RuleText, cls).__new__(cls, value)

    def __init__(self, value):
        self.refs = []
        for item in self.see_rule.findall(value):
            self.refs.append(RuleRef(item[0]))
        for item in self.see_section.findall(value):
            self.refs.append(SectionRef(item[0]))


class Example(str):
    pattern = re.compile(r"(?P<example>Example: (?P<text>.+))")

    def __new__(cls, value, *args, **kwargs):
        return super(Example, cls).__new__(cls, value)

    def __init__(self, value):
        res = self.pattern.match(value)
        if not res:
            raise ValueError("String is not an example")
        self.text = RuleText(res.group("text"))


class Rule(MightstoneModel):
    ref: RuleRef = None
    text: RuleText = None
    examples: List[Example] = []

    @classmethod
    def parse_text(cls, value):
        pattern = re.compile(RuleRef.regex.pattern + r"\s+(?P<text>\w+.*)")

        res = pattern.match(value)
        if not res:
            raise ValueError("String is not a rule")

        return Rule(
            ref=RuleRef(res.group("reference")), text=RuleText(res.group("text"))
        )


class Effectiveness(str):
    pattern = re.compile(
        r"(?P<effective>These rules are effective as of"
        r" (?P<date>(?P<month>\w+) (?P<day>\d+), (?P<year>\d{4})).)"
    )

    def __new__(cls, value, *args, **kwargs):
        return super(Effectiveness, cls).__new__(cls, value)

    def __init__(self, value):
        res = self.pattern.match(value)
        if not res:
            raise ValueError("String is not an example")
        self.date = datetime.strptime(res.group("date"), "%B %d, %Y").date()


class Ruleset(MightstoneModel, Mapping):
    rules: Dict[str, Rule] = dict()
    last_rule: Rule = None

    def __getitem__(self, k: str) -> Rule:
        return self.rules[k]

    def __len__(self) -> int:
        return len(self.rules)

    def parse_text(self, value: str):
        for line in value.splitlines():
            try:
                rule = Rule.parse_text(line)
                self.rules[rule.ref.canonical] = rule
                self.last_rule = rule
                continue
            except ValueError:
                pass

            try:
                self.rules[self.last_rule.ref.canonical].examples.append(Example(line))
                continue
            except (ValueError, AttributeError):
                pass

    def search(self, string: str):
        return [
            item for item in self.rules.values() if string.lower() in item.text.lower()
        ]

    def range(self, low: str, up: str = None):
        low = RuleRef(low)
        if not up:
            up = RuleRef(low).next()
        else:
            up = RuleRef(up)

        return [item for item in self.rules.values() if up > item.ref >= low]

    def index(self):
        self.rules = dict(sorted(self.rules.items()))


class Term(MightstoneModel):
    term: str
    description: RuleText


class Glossary(MightstoneModel, Mapping):
    terms: Dict[str, Term] = {}

    def __getitem__(self, k: str) -> Term:
        return self.terms[k.lower()]

    def __len__(self) -> int:
        return len(self.terms)

    def add(self, term, text):
        self.terms[term.lower()] = Term(description=RuleText(text), term=term)

    def search(self, string):
        return [
            item
            for item in self.terms.values()
            if string.lower() in item.term.lower()
            or string.lower() in item.description.lower()
        ]

    def index(self):
        self.terms = dict(sorted(self.terms.items()))


class ComprehensiveRules(MightstoneModel):
    effective: date = None
    ruleset: Ruleset = Ruleset()
    glossary: Glossary = Glossary()

    def search(self, string):
        found = []
        found.extend(self.ruleset.search(string))
        found.extend(self.glossary.search(string))
        return found

    @classmethod
    def from_text(cls, buffer: TextIO):
        cr = ComprehensiveRules()
        in_glossary = False
        in_credits = False
        buffer2 = StringIO("\n".join(buffer.read().splitlines()))

        for line in buffer2:
            line = line.strip()
            if not line:
                # Ignore empty lines
                continue

            if not cr.effective:
                # No need to search for effectiveness once found
                try:
                    cr.effective = Effectiveness(line)
                    continue
                except ValueError:
                    ...

            if not in_glossary:
                if "100.1" in cr.ruleset.rules and line == "Glossary":
                    in_glossary = True
                    continue

                cr.ruleset.parse_text(line)
                continue

            if not in_credits:
                if len(cr.glossary.terms) and line == "Credits":
                    in_credits = True
                    continue

                text = "\n".join(
                    [x.strip() for x in takewhile(lambda x: x.strip() != "", buffer2)]
                )
                cr.glossary.add(line, text)
                continue

        cr.ruleset.index()
        cr.glossary.index()

        return cr

    @classmethod
    def from_file(cls, path):
        with open(path, "r") as f:
            return cls.from_text(f)

    @classmethod
    def from_url(cls, url: str):
        with requests.get(url) as f:
            f.raise_for_status()
            try:
                content = StringIO(f.content.decode("UTF-8"))
            except UnicodeDecodeError:
                content = StringIO(f.content.decode("iso-8859-1"))

            return cls.from_text(content)

    @classmethod
    def from_latest(cls):
        latest = cls.latest()
        return cls.from_url(latest)

    @classmethod
    def latest(cls):
        pattern = re.compile(r"https://media.wizards.com/.*/MagicComp.+\.txt")
        with requests.get("https://magic.wizards.com/en/rules") as f:
            f.raise_for_status()
            res = pattern.search(f.text)
            if res:
                return res.group(0).replace(" ", "%20")
            raise RuntimeError("Unable to find URL of the last comprehensive rules")

    @classmethod
    async def explore(cls, f: date, t: date = None, concurrency=3):
        """
        AFAIK Wizards don’t support an historic index of previous rules.
        This method will force try every possible rule using the current format:

        https://media.wizards.com/YYYY/downloads/MagicComp%20Rules%20{YYYY}{MM}{DD}.txt
        :param f: The min date to scan
        :param t: The max date to scan (defaults to today)
        :param concurrency: The max number of concurrent HTTP requests
        :return: A list of existing rules url
        """
        if not t:
            t = date.today()

        urls = []
        for n in range(int((t - f).days)):
            d = f + timedelta(n)
            urls.append(d.strftime("/%Y/downloads/MagicComp%%20Rules%%20%Y%m%d.txt"))
            urls.append(d.strftime("/%Y/downloads/MagicCompRules%%20%Y%m%d.txt"))
        map(lambda x: f"https://media.wizards.com{x}", urls)

        found = []
        sem = asyncio.Semaphore(concurrency)

        async def test_url(session, url):
            async with sem:
                logger.debug("GET %s", url)
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.info("Found %s", url)
                        found.append(url)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                task = asyncio.ensure_future(test_url(session, url))
                tasks.append(task)
            await asyncio.gather(*tasks, return_exceptions=True)

        return found

    def diff(self, cr: "ComprehensiveRules"):
        """
        Compare two comprehensive rule set for change in rules and terms

        For both, terms and rules, provide a dict for:
         - `added` a dict of added object
         - `changed` a dict of dict (before/after) object
         - `removed` a dict of removed object

        :param cr: An other comprehensive rule set to compare
        :return: a dict of changes
        """
        if cr.effective > self.effective:
            older = self
            newer = cr
        else:
            older = cr
            newer = self

        diff = defaultdict(lambda: {"added": {}, "removed": {}, "changed": {}})

        new_rules = set(newer.ruleset.rules)
        old_rules = set(older.ruleset.rules)
        moved_from = {}

        # Check for inclusion, search for same text, but new index
        for ref in new_rules - old_rules:
            current = RuleRef(ref)
            previous = current.prev()
            while previous:
                if (
                    older.ruleset[previous.canonical].text
                    == newer.ruleset[current.canonical].text
                ):
                    moved_from[previous.canonical] = current.canonical
                    diff["rules"]["changed"][current.canonical] = {
                        "before": older.ruleset[previous.canonical],
                        "after": newer.ruleset[current.canonical],
                    }
                    current = previous
                    previous = current.prev()
                else:
                    diff["rules"]["added"][current.canonical] = newer.ruleset[
                        current.canonical
                    ]
                    break
        for ref in old_rules - new_rules:
            diff["rules"]["removed"][ref] = older.ruleset[ref]
        for ref in new_rules.intersection(old_rules):
            if newer.ruleset[ref].text != older.ruleset[ref].text:
                if ref not in moved_from:
                    diff["rules"]["changed"][ref] = {
                        "before": older.ruleset[ref],
                        "after": newer.ruleset[ref],
                    }

        new_terms = set(newer.glossary.terms)
        old_terms = set(older.glossary.terms)
        for ref in new_terms - old_terms:
            diff["terms"]["added"][ref] = newer.glossary[ref]
        for ref in old_terms - new_terms:
            diff["terms"]["removed"][ref] = older.glossary[ref]
        for ref in new_terms.intersection(old_terms):
            if newer.glossary[ref].description != older.glossary[ref].description:
                diff["terms"]["changed"][ref] = {
                    "before": older.glossary[ref],
                    "after": newer.glossary[ref],
                }

        return diff
