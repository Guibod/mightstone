from mightstone.app import Mightstone
from mightstone.services.edhrec import PageCompanions

mightstone = Mightstone()


companions: PageCompanions = mightstone.edhrec_static.companions()  # type: ignore
print(companions.model_dump_json(indent=2))
