from pydantic import BaseModel


class MightstoneModel(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))
