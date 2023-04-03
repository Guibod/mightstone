from mightstone.app import Mightstone

m = Mightstone()
found = list(m.scryfall.search("boseiju"))

print("boseiju matches:")
for card in found:
    print(f" - {card}")

print(f"Found {len(found)} instances of Boseiju")

print(list([x.name for x in m.scryfall.search("thalia")]))
