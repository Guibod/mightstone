from mightstone.app import Mightstone
from mightstone.ass import aiterator_to_list

scryfall = Mightstone().scryfall
found = aiterator_to_list(scryfall.search_async("boseiju"))

print(f"Found {len(found)} instances of Boseiju")
for card in found:
    print(f" - {card}")
