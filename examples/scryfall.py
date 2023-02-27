from mightstone.ass import stream_as_list
from mightstone.services.scryfall import Scryfall

scryfall = Scryfall()
found = stream_as_list(scryfall.search("boseiju"))

print(f"Found {len(found)} instances of Boseiju")
for card in found:
    print(f" - {card}")
