from mightstone.ass import aiterator_to_list
from mightstone.services.scryfall import Scryfall

scryfall = Scryfall()
found = aiterator_to_list(scryfall.search_async("boseiju"))

print(f"Found {len(found)} instances of Boseiju")
for card in found:
    print(f" - {card}")
