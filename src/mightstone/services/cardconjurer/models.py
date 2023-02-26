from enum import Enum
from typing import (
    Annotated,
    Any,
    Dict,
    ForwardRef,
    Generator,
    List,
    Literal,
    Optional,
    Pattern,
    Union,
)

from pydantic.color import Color
from pydantic.config import Extra
from pydantic.fields import Field
from pydantic.networks import AnyUrl

from mightstone.core import MightstoneModel


class LayerTypes(str, Enum):
    GROUP = "group"
    IMAGE = "image"
    TEXT = "text"


class Filters(str, Enum):
    COLOR_OVERLAY = "colorOverlay"
    SHADOW = "shadow"


class HorizontalAlign(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class VerticalAlign(str, Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class BoundType(str, Enum):
    FIT = "fit"
    FILL = "fill"


class Tags(Enum):
    """
    Another important note is that many text and image layers have the tags "editable",
    and there are two groups tagged "new-image-group" and "new-text-group". These tags
    tell the UI which layers should be presented as editable, and which layer groups
    should store newly-added layers.
    """

    EDITABLE = "editable"
    DRAGGABLE = "draggable"
    NEW_IMAGE_GROUP = "new-image-group"
    NEW_TEXT_GROUP = "new-text-group"
    NAME = "name"


class TemplateRef(MightstoneModel):
    url: str


class Dependencies(MightstoneModel):
    extensions: List[str] = []
    template: Optional[TemplateRef]


class Bound(MightstoneModel):
    x: int
    y: int
    width: int
    height: int
    type: BoundType
    horizontal: HorizontalAlign
    vertical: VerticalAlign


class Layer(MightstoneModel):
    type: Any
    name: Optional[str]
    tags: Optional[List[Tags]]

    def find_all(
        self,
        model=None,
        tag: Tags = None,
        name: Union[str, Pattern] = None,
        type: LayerTypes = None,
    ) -> Generator["Layer", None, None]:
        # TODO: sort by Z index by default
        for layer in self._recurse():
            if model and not isinstance(layer, model):
                continue

            if isinstance(name, Pattern):
                try:
                    if not name.match(layer.name):
                        continue
                except TypeError:
                    continue
            elif name and layer.name != name:
                continue

            if tag:
                try:
                    if not layer.tags:
                        continue
                    if tag not in layer.tags:
                        continue
                except AttributeError:
                    continue
            if type and type != layer.type:
                continue
            yield layer

    def find(
        self, model=None, tag: str = None, name: str = None, type: LayerTypes = None
    ) -> "Layer":
        it = self.find_all(model, tag, name, type)
        return next(it, None)

    def _recurse(self) -> Generator["Layer", None, None]:
        try:
            for child in self.children:
                yield from child._recurse()
        except AttributeError:
            ...
        try:
            for mask in self.masks:
                yield mask
        except (AttributeError, TypeError):
            ...

        yield self


class Mask(MightstoneModel):
    type: Literal[LayerTypes.IMAGE]
    name: str
    src: str


class Variant(MightstoneModel):
    name: str
    src: str
    thumb: str
    x: Optional[int]


class FilterOverlay(MightstoneModel):
    type: Literal[Filters.COLOR_OVERLAY]
    color: Color


class FilterShadow(MightstoneModel):
    type: Literal[Filters.SHADOW]
    color: Color = Color("black")
    x: int
    y: int


Filter = Annotated[Union[FilterShadow, FilterOverlay], Field(discriminator="type")]


class Image(Layer):
    """
    A layer composed of an image (One of the 3 possible layer types)
    """

    type: Literal[LayerTypes.IMAGE]
    src: str
    x: int = 0
    y: int = 0
    z: int = 0
    width: int = 100
    height: int = 100
    thumb: Optional[str]
    bounds: Optional[Bound]
    masks: Optional[List[Mask]]
    opacity: Optional[float]
    filters: Optional[List[Filter]]


class Text(Layer):
    """
    A layer composed of a text (One of the 3 possible layer types)
    """

    type: Literal[LayerTypes.TEXT]
    text: str
    font: Optional[str]
    color: Color = Color("#FFFFFF")
    oneLine: bool = False
    align: Optional[HorizontalAlign] = HorizontalAlign.LEFT
    verticalAlign: Optional[VerticalAlign] = VerticalAlign.CENTER
    lineHeightScale: float = 1
    fontWeight: Optional[str]  # bold
    rotation: int = 0
    size: int
    opacity: Optional[float]
    x: int
    y: int
    width: int
    height: int
    textCodesOnly: bool = False
    filters: Optional[List[Union[FilterShadow, FilterOverlay]]]


class CardConjurerRootItem(MightstoneModel):
    asset_root_url: Optional[AnyUrl]
    """
    Not part of CardConjurer model
    This allow to re-contextualize relative path and build proper urls
    """


Group = ForwardRef("Group")
AnyLayer = Annotated[Union[Group, Text, Image], Field(discriminator="type")]


class Group(Layer):
    """
    A layer composed of a list of other layers (One of the 3 possible layer types)
    """

    type: Literal[LayerTypes.GROUP]
    children: List[AnyLayer] = []


class Card(CardConjurerRootItem):
    """
    A Card as described in Card Conjurer JSON
    """

    name: str
    width: int
    height: int
    corners: int = 0
    marginX: int = 0
    marginY: int = 0
    dependencies: Dependencies = Dependencies()
    data: Group = Group(type=LayerTypes.GROUP)

    def find(self, **kwargs):
        return self.data.find(**kwargs)

    def find_all(self, **kwargs):
        return self.data.find_all(**kwargs)


class TemplateMetaData(MightstoneModel):
    """
    This metadata is entirely optional, but it helps describe what the template is for,
    who made it, and how updated it is.
    """

    name: Optional[str]
    game: Optional[str]
    creator: Optional[str]
    created: Optional[str]  # TODO: date January 7, 2022
    updated: Optional[str]  # TODO: date January 7, 2022


class TemplateContextImageSet(MightstoneModel):
    """
    The goal of an image set is to describe how to add an image layer for each
    available image in your template. They can organize your images into distinct
    groups that share common traits, and can remove certain duplicated information.
    """

    prototype: Dict[str, Any]
    variants: List[Variant]
    masks: Optional[List[Mask]]


class TemplateFont(MightstoneModel):
    """
    Fonts are nice and simple. All you define here are the names and URLs of your
    fonts. You can also declare the "weight" and "style" if you have variants of
    fonts with the same name.
    """

    name: str
    src: str
    weight: Optional[str]
    style: Optional[str]


class Symbol(MightstoneModel, extra=Extra.allow):
    src: str
    name: str
    scale: float = 1
    spacing: float = 0.05
    verticalShift: float = 0.05


class TemplateSymbol(MightstoneModel):
    src: str
    name: Union[List[str], str]

    def to_dict(self, prefix: str, prototype: dict, unique=False) -> Dict[str, Symbol]:
        names = [self.name] if isinstance(self.name, str) else self.name
        symbol = Symbol(src=prefix + self.src, name=names[0], **prototype)
        if unique:
            return {names[0]: symbol}
        return {name: symbol for name in names}


class SymbolSet(MightstoneModel):
    name: str
    symbols: List[TemplateSymbol]
    prototype: Dict[str, Any]
    srcPrefix: str

    def to_dict(self, unique=False) -> Dict[str, Symbol]:
        return dict(
            pair
            for s in self.symbols
            for pair in s.to_dict(self.srcPrefix, self.prototype, unique).items()
        )


class TemplateContext(MightstoneModel):
    """
    The Template Context is pretty large, but here are the main sections. We'll break
    each one down individually, in detail.
    """

    ui: Any = None
    image_sets: List[TemplateContextImageSet] = Field(alias="imageSets", default=[])
    fonts: List[TemplateFont] = []
    symbol_sets: List[SymbolSet] = Field(alias="symbolSets", default=[])

    def symbols(self, unique=False) -> Dict[str, Symbol]:
        return dict(
            (k.lower(), v)
            for ss in self.symbol_sets
            for k, v in ss.to_dict(unique).items()
        )


class Template(CardConjurerRootItem):
    """
    A Template as described in Card Conjurer JSON
    """

    metadata: TemplateMetaData
    context: TemplateContext
    card: Card

    @classmethod
    def dummy(cls):
        """
        :return: A dummy template, with nothing in it
        """
        return Template(
            metadata=TemplateMetaData(),
            context=TemplateContext(),
            card=Card(name="Dummy", width=100, height=100),
        )


Group.update_forward_refs()
