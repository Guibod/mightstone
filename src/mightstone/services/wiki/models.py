import html
import re
from typing import Optional, Union

from mightstone.core import MightstoneModel


class WikiTag(MightstoneModel):
    tag: str
    extra: Optional["WikiString"] = None
    kwargs: dict[str, "WikiString"] = {}
    args: list["WikiString"] = []

    def get_kwarg(self, keys: list[str]) -> Union[str, None]:
        for key in keys:
            if key in self.kwargs:
                return str(self.kwargs[key])

        return None

    def get_arg(self, index: int) -> Union[str, None]:
        try:
            return str(self.args[index])
        except IndexError:
            return None

    def __str__(self):
        parts = [self.tag]
        if self.extra:
            parts = [f"{self.tag} {self.extra}"]

        if self.args:
            parts.append(" | ".join(map(str, self.args)))

        if self.kwargs:
            parts.append(
                " | ".join(map(lambda kv: f"{kv[0]} = {kv[1]}", self.kwargs.items()))
            )

        return "{{ " + " | ".join(parts) + " }}"


WIKILINK = re.compile(r"\[([^]]+)]")


class WikiString(MightstoneModel):
    tokens: list[Union[str, WikiTag]] = list()

    def __str__(self):
        return " ".join(map(WikiString.escape_part, self.tokens))

    @staticmethod
    def escape_part(part) -> str:
        if isinstance(part, str):
            return html.unescape(WIKILINK.sub(r"\1", part))
        return str(part)

    @staticmethod
    def from_string(string: str):
        return WikiString(tokens=[string])
