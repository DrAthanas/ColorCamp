"""Mapping of hashes to Colors"""

from __future__ import annotations
from typing import Dict, Optional, Any, Hashable
from collections import UserDict

from colorcamp.color_objects._color_metadata import MetaColor
from colorcamp.common.types import ColorSpace
from colorcamp._settings import settings
from .color_space import BaseColor

DIV_TEMPLATE = """
<tr>
    <td>{text}</td>
    <td style="
        width: {width}px; 
        height: {height}px; 
        background-color: {css};
        align-items: center; 
        justify-content: center;
    "></td>
</tr>
"""


class Map(UserDict, MetaColor):
    """A color object to represent color Mappings"""

    def __init__(
        self,
        color_map: Dict[Hashable, BaseColor],
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """color Maps are used for explicit categorical data

        Parameters
        ----------
        color_map : Dict[Hashable, BaseColor]
            A dictionary with colors as values
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """

        self.name = name
        self.description = description
        self.metadata = metadata  # type: ignore

        super().__init__(color_map)

    def to_dict(self) -> dict:
        """create a dictionary of all Map attributes

        Returns
        -------
        Dict[str, Any]
            dictionary with the underlying Map representation
        """

        return {
            "type": "Map",
            **self.info(),
            "color_map": {name: color.to_dict() for name, color in self.items()},
        }

    @classmethod
    def from_dict(cls, map_dict: Dict[str, Any], color_type: Optional[ColorSpace] = None) -> Map:
        """create a new Map object from a Map dictionary

        Parameters
        ----------
        map_dict : Dict[str, Any]
            a Map dictionary
        color_type : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass). If None is supplied the default representation is used, by default None

        Returns
        -------
        Map
            A new Map object
        """

        if color_type is None:
            color_type = settings.default_color_type  # type: ignore

        ## init colors
        color_map = {name: BaseColor.from_dict(color, color_type) for name, color in map_dict["color_map"].items()}

        return cls(
            color_map=color_map,
            name=map_dict.get("name"),
            description=map_dict.get("description"),
            metadata=map_dict.get("metadata"),
        )

    def __setitem__(self, key, value):
        if not isinstance(value, BaseColor):
            raise TypeError("colors must by a Color or proper subclass")

        super().__setitem__(key, value)

    def __repr__(self) -> str:
        return f"Map{super().__repr__()}"

    def _repr_html_(self) -> str:
        html_string = '<table class="table">\n'

        html_string += "\n".join(
            [DIV_TEMPLATE.format(text=key, css=color.css(), height=15, width=15) for key, color in self.items()]
        )
        html_string += "</table>"

        return html_string
