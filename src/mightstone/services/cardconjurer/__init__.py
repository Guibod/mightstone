import asyncio
import base64
import datetime
import os.path
import re
import textwrap
from collections import defaultdict
from io import BytesIO
from typing import Dict, Generic, TypeVar, Union
from urllib.parse import urlparse

import aiofiles
import PIL.Image
from httpx import HTTPStatusError
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from pydantic.color import Color
from pydantic.error_wrappers import ValidationError

from mightstone import logger
from mightstone.services import MightstoneHttpClient, ServiceError
from mightstone.services.cardconjurer.models import (
    Card,
    FilterOverlay,
    FilterShadow,
    HorizontalAlign,
)
from mightstone.services.cardconjurer.models import Image as CCImage
from mightstone.services.cardconjurer.models import (
    LayerTypes,
    Symbol,
    Template,
    TemplateFont,
    Text,
    VerticalAlign,
)

T = TypeVar("T")


base64_prefix = re.compile("^data:image/(?P<mime>.+);base64,")
inline_icon = re.compile(r"(?P<icon>{(?P<name>\w+)})")
inline_icon_sep = re.compile(r"({\w+})")


class CardConjurer(MightstoneHttpClient):
    """
    Card Conjurer client
    """

    base_url = None
    default_font = "LiberationMono-Regular.ttf"

    def __init__(self, default_font=None, **kwargs):
        super().__init__(**kwargs)

        self.assets_images: Dict[str, Image.Image] = {}
        self.assets_fonts: Dict[str, BytesIO] = {}
        if not default_font:
            default_font = os.path.join(
                os.path.dirname(__file__), "../../assets/LiberationMono-Regular.ttf"
            )
        self.default_font = os.path.realpath(default_font)
        self.clear()

    def clear(self):
        with open(self.default_font, "rb") as f:
            default_font = BytesIO(f.read())
        self.assets_fonts = defaultdict(lambda: default_font)
        self.assets_images = {}

    async def template(self, url_or_path) -> Template:
        """
        Open a ``Template``, local or through HTTP

        :param url_or_path: A path or an url
        :return: ``Template`` instance
        """
        if urlparse(url_or_path).scheme != "":
            return await self._url(Template, url_or_path)
        return await self._file(Template, url_or_path)

    async def card(self, url_or_path) -> Card:
        """
        Open a ``Card``, local or through HTTP

        :param url_or_path: A path or an url
        :return: ``Card`` instance
        """
        if urlparse(url_or_path).scheme != "":
            return await self._url(Card, url_or_path)
        return await self._file(Card, url_or_path)

    async def render(self, card: Card, output=None) -> PIL.Image.Image:
        """
        Render a card object into a PIL Image

        :param card: Card model from Card Conjurer
        :param output: A path or a file like object for writing
        :return: A PIL Image object
        """
        # TODO: Use async to download assets first, then build the image
        image = Image.new("RGBA", (card.width, card.height), (255, 255, 255, 0))

        coros = []
        template = Template.dummy()
        if card.dependencies.template.url:
            template_path = card.asset_root_url + "/" + card.dependencies.template.url
            try:
                template = await self.template(template_path)
            except FileNotFoundError:
                raise ServiceError(
                    f"Unable to find parent template for {card.name},"
                    f" {template_path} was composed from the card path. Please try to"
                    " define a custom asset_root_url for this card."
                )
            for font in template.context.fonts:
                coros.append(self._fetch_font(font, card.asset_root_url))
            for symbol in template.context.symbols(True).values():
                coros.append(self._fetch_image(symbol, card.asset_root_url))

        for layer in card.find_all(type=LayerTypes.IMAGE):
            coros.append(self._fetch_image(layer, card.asset_root_url))

        await asyncio.gather(*coros)

        for layer in card.find_all(type=LayerTypes.IMAGE, model=CCImage):
            im = self.assets_images[layer.src]
            if layer.opacity:
                apply_opacity(im, layer.opacity)

            if layer.width and layer.height:
                im = im.resize((layer.width, layer.height))

            # # TODO: implement bounds
            # # TODO: implement margins
            if layer.masks:
                clean_layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
                for m in layer.masks:
                    im = Image.composite(im, clean_layer, self.assets_images[m.src])

            if layer.filters:
                for f in layer.filters:
                    if isinstance(f, FilterOverlay):
                        im = apply_overlay(im, f.color)

                    if isinstance(f, FilterShadow):
                        im = apply_shadow(im, f.color, f.x, f.y)

            image.alpha_composite(im, (layer.x, layer.y))

        for layer in card.find_all(type=LayerTypes.TEXT):
            if not layer.text:
                continue

            im = await self._add_text2(layer, template.context.symbols())

            if layer.opacity:
                apply_opacity(im, layer.opacity)

            if layer.filters:
                for f in layer.filters:
                    if isinstance(f, FilterOverlay):
                        im = apply_overlay(im, f.color)

                    if isinstance(f, FilterShadow):
                        im = apply_shadow(im, f.color, f.x, f.y)

            image.alpha_composite(im, (layer.x, layer.y))

        if card.corners:
            image = self._add_corners(image, 60)

        if output:
            image.save(output)

        return image

    async def _file(self, model: Generic[T], path: str) -> T:
        """
        Reads a Card Conjurer model from a local file using asyncio

        :param model: The model (either ``Card`` or ``Template``)
        :param path: The local path to read from
        :return: Model validated instance
        """
        try:
            async with aiofiles.open(path, encoding="utf-8") as f:
                x = model.parse_raw(await f.read())
                x.asset_root_url = os.path.dirname(path)
                return x
        except ValidationError as e:
            raise ServiceError(
                message=f"Failed to validate {Template} data, {e.errors()}",
                url=path,
                status=None,
                data=e,
            )

    async def _url(self, model: Generic[T], url: str) -> T:
        try:
            f = await self.client.get(url)
            f.raise_for_status()
            x = model.parse_raw(f.content)
            x.asset_root_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(url))
            return x
        except ValidationError as e:
            raise ServiceError(
                message=f"Failed to validate {Template} data, {e.errors()}",
                url=url,
                method="GET",
                status=None,
                data=e,
            )
        except HTTPStatusError as e:
            raise ServiceError(
                message="Failed to fetch CardConjurer template",
                url=e.request.url,
                method=e.request.method,
                status=e.response.status_code,
                data=None,
            )

    async def _fetch_font(self, font: TemplateFont, base_uri: str = None):
        uri = font.src
        if base_uri:
            uri = base_uri + "/" + font.src

        parsed_uri = urlparse(uri, "file")
        logger.info("Fetching font %s", font)
        if parsed_uri.scheme == "file":
            async with aiofiles.open(uri) as f:
                buffer = BytesIO(await f.read())
        elif parsed_uri.scheme in ("http", "https"):
            f = await self.client.get(uri)
            buffer = BytesIO(f.content)
        else:
            raise RuntimeError(f"Unknown scheme {parsed_uri.scheme}")

        logger.info("%s successfully fetched", font)
        self.assets_fonts[font.name] = buffer

    async def _fetch_image(self, img: Union[CCImage, Symbol], base_uri: str = None):
        if base64_prefix.match(img.src):
            logger.info("Using BASE64 image")
            fo = BytesIO(base64.b64decode(base64_prefix.sub("", img.src)))
            self.assets_images[img.src] = self._image_potentially_from_svg(fo)
            return

        uri = img.src
        if base_uri:
            uri = base_uri + "/" + img.src

        parsed_uri = urlparse(uri, "file")
        logger.info("Fetching image %s", uri)
        if parsed_uri.scheme == "file":
            async with aiofiles.open(uri) as f:
                self.assets_images[img.src] = self._image_potentially_from_svg(
                    BytesIO(await f.read())
                )
                return

        if parsed_uri.scheme in ("http", "https"):
            f = await self.client.get(uri)
            self.assets_images[img.src] = self._image_potentially_from_svg(
                BytesIO(f.content)
            )
            return

        raise ValueError(f"URI: {uri} scheme is not supported")

    @staticmethod
    def _image_potentially_from_svg(file: BytesIO) -> Image.Image:
        """
        PIL don’t support SVG, fallback to CairoSvg to generate a PNG file.

        :param file: file like object
        :return: file like object
        """
        try:
            return Image.open(file)
        except UnidentifiedImageError:
            file.seek(0)
            import cairosvg

            svg2png_buffer = BytesIO()
            cairosvg.svg2png(file_obj=file, write_to=svg2png_buffer)
            return Image.open(svg2png_buffer)

    async def _add_text2(self, layer: Text, symbols: Dict[str, Symbol], **kwargs):
        im = PIL.Image.new("RGBA", (layer.width, layer.height), (0, 0, 0, 0))
        font_file = self.assets_fonts[layer.font]
        font_file.seek(0)
        font = ImageFont.truetype(font_file, layer.size)
        draw = ImageDraw.Draw(im, "RGBA")

        if layer.align == HorizontalAlign.LEFT:
            anchor = "la"
            origin = 0
        elif layer.align == HorizontalAlign.RIGHT:
            anchor = "ra"
            origin = layer.width
        else:
            if inline_icon_sep.match(layer.text):
                raise ValueError("Centered text with inline icon is not supported")
            anchor = "ma"
            origin = layer.width / 2

        text = coreTextCode(layer.text)
        xy = (origin, 0)
        line_height = round(layer.size * layer.lineHeightScale)
        max_y = 0

        for line in get_wrapped_text(text, font, layer.width).splitlines():
            parts = re.split(inline_icon_sep, line)
            if layer.align == HorizontalAlign.RIGHT:
                parts.reverse()
            for part in parts:
                if not part:
                    continue

                icon = inline_icon.match(part)
                if not icon:
                    bb = draw.textbbox(xy, part, font=font, anchor=anchor)
                    draw.text(
                        xy,
                        part,
                        font=font,
                        anchor=anchor,
                        fill=layer.color.as_rgb_tuple(),
                    )

                    xy = (xy[0] + bb[2] - bb[0], xy[1])
                else:
                    if icon.group("name").lower() not in symbols:
                        raise ValueError(
                            f"Could not resolve symbol {icon.group('name')} in"
                            f" {symbols.keys()}"
                        )

                    symbol = symbols[icon.group("name").lower()]
                    icon_size = (
                        round(symbol.scale * line_height),
                        round(symbol.scale * line_height),
                    )
                    icon_padding = round(icon_size[0] * symbol.spacing)
                    icon_vshift = round(icon_size[0] * symbol.verticalShift)
                    icon_y = (
                        xy[1] + round((layer.size - icon_size[1]) / 2) + icon_vshift
                    )
                    if layer.align == HorizontalAlign.RIGHT:
                        icon_position = (xy[0] - icon_size[0] - icon_padding, icon_y)
                        xy = (icon_position[0] - icon_padding, xy[1])
                    else:
                        icon_position = (xy[0] + icon_padding, icon_y)
                        xy = (xy[0] + icon_size[0] + icon_padding + icon_padding, xy[1])

                    icon = self.assets_images[symbol.src].resize(icon_size)
                    im.alpha_composite(icon, icon_position)

            max_y = xy[1] + line_height
            xy = (origin, max_y)

        if max_y > layer.height:
            # TODO: if too high, retry with smaller font
            pass

        if layer.verticalAlign == VerticalAlign.BOTTOM:
            clean_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
            clean_layer.alpha_composite(im, (0, layer.height - max_y))
            return clean_layer
        elif layer.verticalAlign == VerticalAlign.CENTER:
            clean_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
            clean_layer.alpha_composite(im, (0, round((layer.height - max_y) / 2)))
            return clean_layer

        return im

    @staticmethod
    async def _add_text(image, layer, ttf, max_chars=100):
        # TODO: lineHeightScale
        draw = ImageDraw.Draw(image)
        while True:
            if layer.align == HorizontalAlign.LEFT:
                anchor = "lm"
                xy = (layer.x, layer.y + layer.height / 2)
            elif layer.align == HorizontalAlign.RIGHT:
                anchor = "rm"
                xy = (layer.x + layer.width, layer.y + layer.height / 2)
            else:
                xy = (layer.x + layer.width / 2, layer.y + layer.height / 2)
                anchor = "mm"

            text = coreTextCode(layer.text)
            if not layer.oneLine:
                text = textwrap.fill(text, replace_whitespace=False, width=max_chars)

            bb = draw.textbbox(xy=xy, text=text, font=ttf, anchor=anchor)
            if layer.oneLine:
                break

            if (bb[2] - bb[0]) < layer.width:
                break
            max_chars -= 5

        height = bb[3] - bb[1]
        if layer.verticalAlign == VerticalAlign.TOP:
            xy = (xy[0], xy[0] - height / 2)
        elif layer.align == VerticalAlign.BOTTOM:
            xy = (xy[0], xy[0] + height / 2)

        if layer.filters:
            for f in layer.filters:
                if isinstance(f, FilterShadow):
                    shadow_xy = (xy[0] + f.x, xy[1] + f.y)
                    draw.text(
                        xy=shadow_xy, text=text, font=ttf, anchor=anchor, fill=(0, 0, 0)
                    )

        draw.text(
            xy=xy, text=text, font=ttf, anchor=anchor, fill=layer.color.as_rgb_tuple()
        )

    @staticmethod
    def _add_corners(im, rad):
        circle = Image.new("L", (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)

        w, h = im.size
        alpha = im.getchannel("A")
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))

        im.putalpha(alpha)

        return im


def get_wrapped_text(text: str, font: ImageFont.ImageFont, max_width: int):
    """
    A text wrapper that will wraps a string over a maximum text width for a given font
    and given width in an image

    :param text: The text to wrap
    :param font: A pillow ``ImageFont`` instance
    :param max_width: The maximum width your text should fit in
    :return: A wrapped text that will fit in a given width
    """
    lines = [""]
    for line in text.splitlines():
        for word in line.split():
            line = f"{lines[-1]} {word}".strip()
            if font.getlength(line) <= max_width:
                lines[-1] = line
            elif not len(lines[-1]):
                # Don’t split on first item
                lines[-1] = line
            else:
                lines.append(word)
        lines.append("")

    return "\n".join(lines[0:-1])


def coreTextCode(string: str) -> str:
    return (
        string.replace("{year}", str(datetime.date.today().year))
        .replace("{i}", "")
        .replace("{/i}", "")
        .replace("{line}", "\n")
    )


def apply_overlay(im: Image.Image, color: Color):
    clean_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
    overlay = Image.new("RGBA", im.size, color.as_rgb_tuple())
    return Image.composite(overlay, clean_layer, im)


def apply_shadow(im: Image.Image, color, offset_x=0, offset_y=0):
    clean_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
    shadow = Image.new("RGBA", im.size, color=color.as_rgb_tuple())
    clean_layer.paste(shadow, (offset_x, offset_y), mask=im)
    clean_layer.paste(im, (0, 0), mask=im)

    return clean_layer


def apply_opacity(im: Image.Image, opacity):
    alpha = im.getchannel("A")
    im.putalpha(alpha.point(lambda i: (opacity * 256) if i > 0 else 0))
