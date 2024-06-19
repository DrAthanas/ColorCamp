"""Collections of Colors"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from colorcamp._settings import settings
from colorcamp.color_space import BaseColor
from colorcamp.common.types import ColorSpace
from colorcamp.static.html_templates import (
    HTML_NAME_TEMPLATE,
    HTML_REPR_TEMPLATE,
    MIN_HEIGHT,
    MIN_WIDTH,
)

from ._color_group import ColorGroup

__all__ = ["Palette"]


class Palette(ColorGroup, tuple):
    """An object to represent discrete color Palettes"""

    # pylint: disable=W0613
    def __new__(cls, colors, *args, **kwargs):
        if not all((isinstance(color, BaseColor) for color in colors)):
            raise TypeError("colors must by a Color or proper subclass")
        return super().__new__(cls, colors)

    def __init__(
        self,
        colors: Sequence[BaseColor],
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """color Palettes are used for categorical data, themes, and branding

        Parameters
        ----------
        colors : Sequence[BaseColor]
            a sequence of Colors
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """

        self.__current_index = 0

        super().__init__(
            colors,
            name=name,
            description=description,
            metadata=metadata,
        )

    @property
    def colors(self):
        """sequence of Colors"""

        return tuple(self)

    def next(self):
        """returns the current color in the palette and iterates to the next. If at the end will move to the beginning

        Returns
        -------
        Color
        """

        index = self.__current_index
        self.__current_index = (self.__current_index + 1) % len(self)

        return self[index]

    def reverse(self) -> Palette:
        """Return a new palette with the order of the colors reversed

        Returns
        -------
        Palette
        """
        return Palette(colors=self.colors[::-1], **self.info())

    def to_dict(self):
        """Create a dictionary of all Palette attributes

        Returns
        -------
        Dict[str, Any]
            dictionary with the underlying Palette representation
        """

        return {
            "type": "Palette",
            **self.info(),
            "colors": [color.to_dict() for color in self],
        }

    @classmethod
    def from_dict(cls, palette_dict: Dict[str, Any], color_space: Optional[ColorSpace] = None) -> Palette:
        """create a new Palette object from a Palette dictionary

        Parameters
        ----------
        palette_dict : Dict[str, Any]
            a Palette dictionary
        color_space : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass). If None is supplied the default representation is used, by default None

        Returns
        -------
        Palette
            A new Palette object
        """

        if color_space is None:
            color_space = settings.default_color_space  # type: ignore

        ## init colors
        colors = [BaseColor.from_dict(color, color_space) for color in palette_dict["colors"]]

        return cls(
            colors=colors,
            name=palette_dict.get("name"),
            description=palette_dict.get("description"),
            metadata=palette_dict.get("metadata"),
        )

    def to_native(self):
        return tuple([color.native for color in self])

    def __repr__(self) -> str:
        return f"Palette{super().__repr__()}"

    def _repr_html_(self):
        name = "" if self.name is None else HTML_NAME_TEMPLATE.format(name=self.name)

        n_colors = len(self)
        stops = [idx / n_colors for idx in range(n_colors + 1)]
        grad = ", ".join(
            [
                f"{color.hex} {stop:.0%}, {color.hex} {stops[idx+1]:.0%}"
                for idx, (color, stop) in enumerate(zip(self, stops))
            ]
        )
        html_string = HTML_REPR_TEMPLATE.format(
            name=name,
            grad=grad,
            color=f"background-image: linear-gradient(to right, {grad});",
            height=MIN_HEIGHT,
            width=max(min(MIN_HEIGHT * len(self), 450), MIN_WIDTH),
            text="",
        )

        return html_string
