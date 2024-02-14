"""Collections of Colors"""

from __future__ import annotations
from typing import Sequence, Optional, Dict, Any

from colorcamp.common.types import ColorSpace
from colorcamp._settings import settings
from .color_space import BaseColor
from ._color_metadata import MetaColor

DIV_TEMPLATE = """
<div style="
    width: {width}px; 
    height: {height}px; 
    background-color: {css}; 
    display: flex; 
    align-items: center; 
    justify-content: center;
">
</div>
"""


class Palette(MetaColor, tuple):
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

    def to_dict(self):
        """create a dictionary of all Palette attributes

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
    def from_dict(cls, palette_dict: Dict[str, Any], color_type: Optional[ColorSpace] = None) -> Palette:
        """create a new Palette object from a Palette dictionary

        Parameters
        ----------
        palette_dict : Dict[str, Any]
            a Palette dictionary
        color_type : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass). If None is supplied the default representation is used, by default None

        Returns
        -------
        Palette
            A new Palette object
        """

        if color_type is None:
            color_type = settings.default_color_type  # type: ignore

        ## init colors
        colors = [BaseColor.from_dict(color, color_type) for color in palette_dict["colors"]]

        return cls(
            colors=colors,
            name=palette_dict.get("name"),
            description=palette_dict.get("description"),
            metadata=palette_dict.get("metadata"),
        )

    def __repr__(self) -> str:
        return f"Palette{super().__repr__()}"

    def _repr_html_(self) -> str:
        html_string = "\n".join([DIV_TEMPLATE.format(css=color.css(), height=60, width=60) for color in self])

        html_string = f'<div style="display: flex">{html_string}</div>'

        return html_string
