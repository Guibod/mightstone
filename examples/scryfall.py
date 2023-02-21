from dependency_injector.wiring import Provide, inject

from mightstone.ass import stream_as_list
from mightstone.containers import Container
from mightstone.services.scryfall import Scryfall


@inject
def main(
    scry: Scryfall = Provide[Container.scryfall],
) -> None:
    found = stream_as_list(scry.search("boseiju"))

    print(f"Found {len(found)} instances of Boseiju")
    for card in found:
        print(f" - {card}")


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    main()
