import typing
from enum import Enum
from typing import (
    Annotated,
    Any,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Pattern,
    Type,
    TypedDict,
    Union,
    overload,
)

from pydantic.fields import Field
from pydantic_extra_types.color import Color
from typing_extensions import Unpack

from mightstone.core import (
    MightstoneDocument,
    MightstoneModel,
    MightstoneSerializableDocument,
)


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
    template: Optional[TemplateRef] = None


class Bound(MightstoneModel):
    x: int
    y: int
    width: int
    height: int
    type: BoundType
    horizontal: HorizontalAlign
    vertical: VerticalAlign


class LayerSearch(TypedDict):
    model: Optional[Type[MightstoneModel]]
    tag: Optional[Tags]
    name: Optional[Union[str, Pattern]]
    type: Optional[LayerTypes]


class ImageSearch(TypedDict):
    model: Optional[Type[MightstoneModel]]
    tag: Optional[Tags]
    name: Optional[Union[str, Pattern]]
    type: Literal[LayerTypes.IMAGE]


class TextSearch(TypedDict):
    model: Optional[Type[MightstoneModel]]
    tag: Optional[Tags]
    name: Optional[Union[str, Pattern]]
    type: Literal[LayerTypes.TEXT]


class GroupSearch(TypedDict):
    model: Optional[Type[MightstoneModel]]
    tag: Optional[Tags]
    name: Optional[Union[str, Pattern]]
    type: Literal[LayerTypes.GROUP]


class Layer(MightstoneModel):
    type: Any
    name: Optional[str] = None
    tags: Optional[List[Tags]] = None

    @overload
    def find_all(
        self, **kwargs: Unpack[ImageSearch]
    ) -> Generator[Union["Image", "Mask"], None, None]: ...

    @overload
    def find_all(
        self, **kwargs: Unpack[TextSearch]
    ) -> Generator["Text", None, None]: ...
    @overload
    def find_all(
        self, **kwargs: Unpack[GroupSearch]
    ) -> Generator["Group", None, None]: ...

    @overload
    def find_all(
        self, **kwargs: Unpack[LayerSearch]
    ) -> Generator[Union["Image", "Group", "Text", "Mask"], None, None]: ...

    def find_all(
        self, **kwargs: Unpack[LayerSearch]
    ) -> Generator[Union["Image", "Group", "Text", "Mask"], None, None]:
        # TODO: sort by Z index by default
        for layer in self._recurse():
            model = kwargs.get("model")
            if model:
                if not isinstance(layer, model):
                    continue

            name = kwargs.get("name")
            if isinstance(name, Pattern):
                try:
                    if not layer.name:
                        continue
                    elif not name.match(layer.name):
                        continue
                except TypeError:
                    continue
            elif name and layer.name != name:
                continue

            tag = kwargs.get("tag")
            if tag:
                if not hasattr(layer, "tags"):
                    continue

                if not layer.tags:
                    continue

                if tag not in layer.tags:
                    continue

            typ = kwargs.get("type")
            if typ and typ != layer.type:
                continue
            yield layer

    @overload
    def find_one(
        self, **kwargs: Unpack[ImageSearch]
    ) -> Optional[Union["Image", "Mask"]]: ...
    @overload
    def find_one(self, **kwargs: Unpack[TextSearch]) -> Optional["Text"]: ...
    @overload
    def find_one(self, **kwargs: Unpack[GroupSearch]) -> Optional["Group"]: ...

    def find_one(
        self, **kwargs: Unpack[LayerSearch]
    ) -> Optional[Union["Image", "Group", "Text", "Mask"]]:
        it = self.find_all(**kwargs)
        return next(it, None)

    @typing.no_type_check
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
    x: Optional[int] = None


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
    thumb: Optional[str] = None
    bounds: Optional[Bound] = None
    masks: Optional[List[Mask]] = None
    opacity: Optional[float] = None
    filters: Optional[List[Filter]] = None


class Text(Layer):
    """
    A layer composed of a text (One of the 3 possible layer types)
    """

    type: Literal[LayerTypes.TEXT]
    text: str
    font: Optional[str] = None
    color: Color = Color("#FFFFFF")
    oneLine: bool = False
    align: Optional[HorizontalAlign] = HorizontalAlign.LEFT
    verticalAlign: Optional[VerticalAlign] = VerticalAlign.CENTER
    lineHeightScale: float = 1
    fontWeight: Optional[str] = None  # bold
    rotation: int = 0
    size: int
    opacity: Optional[float] = None
    x: int
    y: int
    width: int
    height: int
    textCodesOnly: bool = False
    filters: Optional[List[Union[FilterShadow, FilterOverlay]]] = None


class Group(Layer):
    """
    A layer composed of a list of other layers (One of the 3 possible layer types)
    """

    type: Literal[LayerTypes.GROUP] = LayerTypes.GROUP.value  # type: ignore
    children: List["AnyLayer"] = []


AnyLayer = Annotated[Union[Group, Text, Image], Field(discriminator="type")]


class Card(MightstoneDocument):
    """
    A Card as described in Card Conjurer JSON
    """

    asset_root_url: str = ""
    """
    Not part of CardConjurer model
    This allow to re-contextualize relative path and build proper urls
    """

    name: str
    width: int
    height: int
    corners: int = 0
    marginX: int = 0
    marginY: int = 0
    dependencies: Dependencies = Dependencies()
    data: Group = Group(type=LayerTypes.GROUP)  # type: ignore

    def find_one_layer(self, **kwargs):
        return self.data.find_one(**kwargs)

    def find_many_layer(self, **kwargs):
        return self.data.find_all(**kwargs)

    def find_many_text(self, **kwargs) -> Generator[Text, None, None]:
        return self.data.find_all(type=LayerTypes.TEXT, **kwargs)

    def find_many_images(self, **kwargs) -> Generator[Union[Image, Mask], None, None]:
        return self.data.find_all(type=LayerTypes.IMAGE, **kwargs)

    def find_many_groups(self, **kwargs) -> Generator[Group, None, None]:
        return self.data.find_all(type=LayerTypes.GROUP, **kwargs)


class SerializableCard(Card, MightstoneSerializableDocument): ...


class TemplateMetaData(MightstoneModel):
    """
    This metadata is entirely optional, but it helps describe what the template is for,
    who made it, and how updated it is.
    """

    name: Optional[str] = None
    game: Optional[str] = None
    creator: Optional[str] = None
    created: Optional[str] = None  # TODO: date January 7, 2022
    updated: Optional[str] = None  # TODO: date January 7, 2022


class TemplateContextImageSet(MightstoneModel):
    """
    The goal of an image set is to describe how to add an image layer for each
    available image in your template. They can organize your images into distinct
    groups that share common traits, and can remove certain duplicated information.
    """

    prototype: Dict[str, Any]
    variants: List[Variant]
    masks: Optional[List[Mask]] = None


class TemplateFont(MightstoneModel):
    """
    Fonts are nice and simple. All you define here are the names and URLs of your
    fonts. You can also declare the "weight" and "style" if you have variants of
    fonts with the same name.
    """

    name: str
    src: str
    weight: Optional[str] = None
    style: Optional[str] = None


class Symbol(MightstoneModel, extra="allow"):
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

    license: Optional[dict] = None
    image_sets: List[TemplateContextImageSet] = Field(alias="imageSets", default=[])
    fonts: List[TemplateFont] = []
    symbol_sets: List[SymbolSet] = Field(alias="symbolSets", default=[])

    def symbols(self, unique=False) -> Dict[str, Symbol]:
        return dict(
            (k.lower(), v)
            for ss in self.symbol_sets
            for k, v in ss.to_dict(unique).items()
        )


class Template(MightstoneDocument):
    """
    A Template as described in Card Conjurer JSON
    """

    asset_root_url: str = ""
    """
    Not part of CardConjurer model
    This allow to re-contextualize relative path and build proper urls
    """

    name: str
    context: TemplateContext
    card: Card

    @classmethod
    def dummy(cls):
        """
        :return: A dummy template, with nothing in it
        """
        return Template(
            name="Dummy",
            context=TemplateContext(),
            card=Card(name="Dummy", width=100, height=100),
        )


class SerializableTemplate(Template, MightstoneSerializableDocument): ...


Group.model_rebuild()
