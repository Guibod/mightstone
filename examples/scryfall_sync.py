"""
This example demonstrate the behavior of Mightstone in a synchronous context

random() method is an alias for random() using asgiref’s async_to_sync feature
search() method is an alias for search() using asgiref’s async_to_sync feature
"""

from typing import Iterable

from mightstone import Mightstone
from mightstone.services.scryfall import Card

mightstone = Mightstone()
card: Card = mightstone.scryfall.random()  # type: ignore

print(f"The random card is {card.name} ({card.id})")

brushwaggs: Iterable[Card] = mightstone.scryfall.search("brushwagg")  # type: ignore

for i, brushwagg in enumerate(brushwaggs):
    print(f"Brushwagg {i} is {brushwagg.name} from {brushwagg.set_code}")
