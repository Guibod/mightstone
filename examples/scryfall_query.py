from mightstone.services.scryfall.query import Query, Term

q = Query("f:modern order:rarity direction:asc") & Query("lang:japanese")

print("Recomposed (all explicit)")
print(q.to_string())

print("Recomposed (simplified)")
print(q.to_string(True))

assert isinstance(q[0], Term)
assert q[0].keyword.value == "format"
assert q[0].comparator.value == ":"
assert q[0].value == "modern"

assert isinstance(q[1], Term)
assert isinstance(q[2], Term)

xor = Query("t:creature") ^ Query("t:enchantment")

print("Recomposed (all explicit)")
print(xor.to_string())

print("Recomposed (simplified)")
print(xor.to_string(True))
