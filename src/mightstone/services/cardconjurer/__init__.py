import asyncio
import base64
import datetime
import os.path
import re
import textwrap
from collections import defaultdict
from io import BytesIO
from typing import Dict, Generic, TypeVar
from urllib.parse import urlparse

import aiofiles
import PIL.Image
from httpx import HTTPStatusError
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
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
    Template,
    TemplateFont,
    VerticalAlign,
)

T = TypeVar("T")


base64_prefix = re.compile("^data:image/(?P<mime>.+);base64,")


class CardConjurer(MightstoneHttpClient):
    """
    Card Conjurer client
    """

    base_url = None
    default_font = "LiberationMono-Regular.ttf"

    def __init__(self, default_font=None, **kwargs):
        super().__init__(**kwargs)

        self.assets_images = None
        self.assets_fonts = None
        if not default_font:
            default_font = os.path.join(
                os.path.dirname(__file__), "../../assets/LiberationMono-Regular.ttf"
            )
        self.default_font = os.path.realpath(default_font)
        self.clear()

    def clear(self):
        with open(self.default_font, "rb") as f:
            default_font = BytesIO(f.read())
        self.assets_fonts: Dict[str, BytesIO] = defaultdict(lambda: default_font)
        self.assets_images: Dict[str, Image] = {}

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

        for layer in card.find_all(type=LayerTypes.IMAGE):
            coros.append(self._fetch_image(layer, card.asset_root_url))

        await asyncio.gather(*coros)

        for layer in card.find_all(type=LayerTypes.IMAGE, model=CCImage):
            im = self.assets_images[id(layer)]
            if layer.opacity:
                alpha = im.getchannel("A")
                im.putalpha(
                    alpha.point(lambda i: (layer.opacity * 256) if i > 0 else 0)
                )

            if layer.width and layer.height:
                im = im.resize((layer.width, layer.height))

            # # TODO: implement bounds
            # # TODO: implement margins
            if layer.masks:
                clean_layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
                for m in layer.masks:
                    im = Image.composite(im, clean_layer, self.assets_images[id(m)])

            if layer.filters:
                clean_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
                for f in layer.filters:
                    if isinstance(f, FilterOverlay):
                        overlay = Image.new("RGBA", im.size, f.color.as_rgb_tuple())
                        im = Image.composite(overlay, clean_layer, im)

            image.alpha_composite(im, (layer.x, layer.y))

        for layer in card.find_all(type=LayerTypes.TEXT):
            if not layer.text:
                continue

            fo = self.assets_fonts[layer.font]
            fo.seek(0)
            ttf = ImageFont.truetype(fo, layer.size)

            await self._add_text(image, layer, ttf)

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

    async def _fetch_image(self, img: CCImage, base_uri: str = None):
        if base64_prefix.match(img.src):
            logger.info("Using BASE64 image")
            fo = BytesIO(base64.b64decode(base64_prefix.sub("", img.src)))
            self.assets_images[id(img)] = self._image_potentially_from_svg(fo)
            return

        uri = img.src
        if base_uri:
            uri = base_uri + "/" + img.src

        parsed_uri = urlparse(uri, "file")
        logger.info("Fetching image %s", uri)
        if parsed_uri.scheme == "file":
            async with aiofiles.open(uri) as f:
                self.assets_images[id(img)] = self._image_potentially_from_svg(
                    BytesIO(await f.read())
                )
                return

        if parsed_uri.scheme in ("http", "https"):
            f = await self.client.get(uri)
            self.assets_images[id(img)] = self._image_potentially_from_svg(
                BytesIO(f.content)
            )
            return

        raise ValueError(f"URI: {uri} scheme is not supported")

    @staticmethod
    def _image_potentially_from_svg(file: BytesIO) -> BytesIO:
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


def coreTextCode(string: str) -> str:
    return (
        string.replace("{year}", str(datetime.date.today().year))
        .replace("{i}", "")
        .replace("{/i}", "")
        .replace("{line}", "\n")
    )
