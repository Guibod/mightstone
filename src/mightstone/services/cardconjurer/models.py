from enum import Enum
from pathlib import Path
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
    extensions: List[str]
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


class FilterOverlay(MightstoneModel):
    type: Literal[Filters.COLOR_OVERLAY]
    color: Color


class FilterShadow(MightstoneModel):
    type: Literal[Filters.SHADOW]
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
    width: Optional[int]
    height: Optional[int]
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
    dependencies: Dependencies
    data: Group

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
    variants: Dict[str, Dict[str, Any]]
    masks: Optional[Dict[str, Mask]]


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


class TemplateSymbol(MightstoneModel):
    src: Path
    name: Union[List[str], str]


class TemplateExtension(MightstoneModel):
    symbols: List[TemplateSymbol]
    prototype: Dict[str, Any]
    srcPrefix: Path


class TemplateContext(MightstoneModel):
    """
    The Template Context is pretty large, but here are the main sections. We'll break
    each one down individually, in detail.
    """

    ui: Any
    image_sets: Dict[str, TemplateContextImageSet] = Field(alias="imageSets")
    fonts: List[TemplateFont] = []
    symbolExtension: Optional[Dict[str, List[TemplateExtension]]]


class Template(CardConjurerRootItem):
    """
    A Template as described in Card Conjurer JSON
    """

    metadata: TemplateMetaData
    context: TemplateContext
    card: Card


Group.update_forward_refs()
