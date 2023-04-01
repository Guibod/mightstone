import asyncio
import json
from datetime import date

from pydantic.json import pydantic_encoder

from mightstone.app import Mightstone
from mightstone.services.wotc.models import RuleRef, RuleText

mightstone = Mightstone()
before_errata = mightstone.rule_explorer.open(
    "https://media.wizards.com/2020/downloads/MagicCompRules%2020200417.txt"
)

errata_companion = asyncio.run(
    mightstone.rule_explorer.open_async(
        "https://media.wizards.com/2020/downloads/MagicCompRules%2020200601.txt"
    )
)
diff = before_errata.diff(errata_companion)
print(json.dumps(diff, default=pydantic_encoder, indent=4))

# rules. new. 116.2g :  A player who has chosen a companion may pay {3} to put that
#                       card from outside the game into their hand.
#        changed: 116.2g -> 116.2h
#        changed: 116.2h -> 116.2i
#        changed: 702.138c: Once you take the special action and put the card ...

# Brute force find all rules between January 1st, 2022 and  February 15, 2023
# using a maximum of 10 requests at a time
print(
    mightstone.rule_explorer.explore(
        date(2020, 1, 1), date(2023, 2, 15), concurrency=10
    )
)

# 'https://media.wizards.com/2020/downloads/MagicCompRules%2020200122.txt',
# 'https://media.wizards.com/2020/downloads/MagicCompRules%2020200417.txt',
# 'https://media.wizards.com/2020/downloads/MagicCompRules%2020200601.txt',
# 'https://media.wizards.com/2020/downloads/MagicCompRules%2020200703.txt',
# 'https://media.wizards.com/2020/downloads/MagicCompRules%2020200807.txt',
# 'https://media.wizards.com/2020/downloads/MagicCompRules%2020200925.txt',
# 'https://media.wizards.com/2020/downloads/MagicCompRules%2020201120.txt',
# 'https://media.wizards.com/2021/downloads/MagicCompRules%2020210202.txt',
# 'https://media.wizards.com/2021/downloads/MagicCompRules%2020210224.txt',
# 'https://media.wizards.com/2021/downloads/MagicCompRules%2020210419.txt',
# 'https://media.wizards.com/2021/downloads/MagicCompRules%2020210609.txt',
# 'https://media.wizards.com/2021/downloads/MagicCompRules%2020210712.txt',
# 'https://media.wizards.com/2021/downloads/MagicCompRules%2020211115.txt',
# 'https://media.wizards.com/2022/downloads/MagicCompRules%2020220218.txt',
# 'https://media.wizards.com/2022/downloads/MagicCompRules%2020220429.txt',
# 'https://media.wizards.com/2022/downloads/MagicCompRules%2020220610.txt',
# 'https://media.wizards.com/2022/downloads/MagicCompRules%2020220708.txt',
# 'https://media.wizards.com/2022/downloads/MagicCompRules%2020220908.txt',
# 'https://media.wizards.com/2022/downloads/MagicCompRules%2020221118.txt',
# 'https://media.wizards.com/2023/downloads/MagicComp%20Rules%2020230203.txt'

# Read the latest comprehensive rules
latest_url = mightstone.rule_explorer.latest()
print(latest_url)

cr = mightstone.rule_explorer.open(latest_url)

# Or simply
# cr = mightstone.rule_explorer.open()

# Or from an URL
# cr = mightstone.rule_explorer.open(
#    "https://media.wizards.com/2022/downloads/MagicCompRules%2020221118.txt")
#
# Or from a local file
# cr = mightstone.rule_explorer.open("/path/to/comprehensive-rules.txt")

# Access effectiveness date (cr.effective is an Effectiveness object)
print(cr.effective.date)  # 2023-02-03

# You can then access a rule by its reference
print(cr.ruleset["120.4a"])

# You can search ruleset for a string
found = cr.ruleset.search("deathtouch")
print(len(found))  # 11
print([rule.ref for rule in found])  # ['120.4a', '122.1b', '701.7b', '702.2.',
# '702.2a', '702.2b', '702.2c', '702.2d',
# '702.2e', '702.2f', '704.5h']

# You can also search glossary
found = cr.glossary.search("deathtouch")
print(len(found))  # 2
print([term.term for term in found])

# A rule is a string, but also provide the ref
print(cr.ruleset["120.4a"].ref)

# A rule reference is a string with properties
print(isinstance(cr.ruleset["120.4a"].ref, str))  # True
print(isinstance(cr.ruleset["120.4a"].ref, RuleRef))  # True
print(cr.ruleset["120.4a"].ref.rule)  # 120
print(cr.ruleset["120.4a"].ref.sub_rule)  # 4
print(cr.ruleset["120.4a"].ref.letter)  # a
print(cr.ruleset["120.4a"].ref.canonical)  # 120.4a
print(cr.ruleset["120.4a"].ref.next())  # 120.4b

# A rule text is a string with properties
print(isinstance(cr.ruleset["120.4a"].text, str))  # True
print(isinstance(cr.ruleset["120.4a"].text, RuleText))  # True
print(cr.ruleset["120.4a"].text.refs)  # ['120.6.', '702.2.']
print(cr.ruleset["120.4a"].text.refs[0])  # 120.6.
print(cr.ruleset["120.4a"].text.refs[0].canonical)  # 120.6
print(cr.ruleset["120.4a"].text)
# First, if an effect that’s causing damage to be dealt states that excess damage
# that would be dealt to a permanent is dealt to another permanent or player instead,
# the damage event is modified accordingly. If the first permanent is a creature,
# the excess damage is the amount of damage in excess of what would be lethal damage,
# taking into account damage already marked on the creature and damage from other
# sources that would be dealt at the same time. (See rule 120.6.) Any amount of
# damage greater than 1 is excess damage if the source dealing that damage to a
# creature has deathtouch. (See rule 702.2.) If the first permanent is a planeswalker,
# the excess damage is the amount of damage in excess of that planeswalker’s loyalty,
# taking into account damage from other sources that would be dealt at the same time.
# If the first permanent is both a creature and a planeswalker, the excess damage is
# the greater of those two amounts.
