"""
This example demonstrate the behavior of Mightstone in a synchronous context

random() method is an alias for random_async() using asgiref’s async_to_sync feature
search() method is an alias for search_async() using asgiref’s async_to_sync feature
"""

from mightstone import Mightstone
from mightstone.services.scryfall import Card

mightstone = Mightstone()
card = mightstone.scryfall.random()

print(f"The random card is {card.name} ({card.id})")

brushwaggs: list[Card] = mightstone.scryfall.search("brushwagg")

for i, brushwagg in enumerate(brushwaggs):
    print(f"Brushwagg {i} is {brushwagg.name} from {brushwagg.set_code}")
