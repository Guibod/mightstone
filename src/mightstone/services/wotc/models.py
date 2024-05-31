import re
from collections import defaultdict
from datetime import datetime
from io import StringIO
from itertools import takewhile
from typing import Any, DefaultDict, Dict, List, Mapping, Optional, TextIO

from pydantic import ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from mightstone.core import MightstoneDocument, MightstoneModel


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

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

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
    def build(
        cls, rule: int, sub_rule: Optional[int] = None, letter: Optional[str] = None
    ):
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

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

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

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    def __new__(cls, value, *args, **kwargs):
        return super(Example, cls).__new__(cls, value)

    def __init__(self, value):
        res = self.pattern.match(value)
        if not res:
            raise ValueError("String is not an example")
        self.text = RuleText(res.group("text"))


class Rule(MightstoneModel):
    ref: RuleRef
    text: RuleText
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

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    def __new__(cls, value, *args, **kwargs):
        return super(Effectiveness, cls).__new__(cls, value)

    def __init__(self, value):
        res = self.pattern.match(value)
        if not res:
            raise ValueError("String is not a valid effectiveness string")
        self.date = datetime.strptime(res.group("date"), "%B %d, %Y").date()


class Ruleset(MightstoneModel):
    rules: Dict[str, Rule] = dict()
    last_rule: Optional[Rule] = None

    # def __iter__(self) -> Iterator[Rule]:  # type: ignore
    #     for rule in self.rules.values():
    #         yield rule

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
                if self.last_rule:
                    self.rules[self.last_rule.ref.canonical].examples.append(
                        Example(line)
                    )
                continue
            except (ValueError, AttributeError):
                pass

    def search(self, string: str):
        return [
            item for item in self.rules.values() if string.lower() in item.text.lower()
        ]

    def range(self, low: str, up: Optional[str] = None):
        low = RuleRef(low)
        if not up:
            up = RuleRef(low).next()
        else:
            up = RuleRef(up)

        if up:
            return [item for item in self.rules.values() if up > item.ref >= low]

        return [item for item in self.rules.values() if item.ref >= low]

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


class ComprehensiveRules(MightstoneDocument):
    effective: Optional[Effectiveness] = None
    ruleset: Ruleset = Ruleset()
    glossary: Glossary = Glossary()
    model_config = ConfigDict(arbitrary_types_allowed=True)  # type: ignore

    def search(self, string):
        found = []
        found.extend(self.ruleset.search(string))
        found.extend(self.glossary.search(string))
        return found

    @classmethod
    def parse(cls, buffer: TextIO):
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
        if cr.effective and self.effective and cr.effective > self.effective:
            older = self
            newer = cr
        else:
            older = cr
            newer = self

        diff: DefaultDict = defaultdict(
            lambda: {"added": {}, "removed": {}, "changed": {}}
        )

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
