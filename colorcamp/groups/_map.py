"""Mapping of hashes to Colors"""

from __future__ import annotations

from typing import Any, Dict, Hashable, Optional

from colorcamp._settings import settings
from colorcamp.color_space import BaseColor
from colorcamp.common.types import ColorSpace
from colorcamp.static.html_templates import MAP_TABLE_ROW

from ._color_group import ColorGroup

__all__ = ["Map"]


# TODO: implement other dict setter methods, update ... etc.
class Map(dict, ColorGroup):
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

        if not all(isinstance(color, BaseColor) for color in color_map.values()):
            raise TypeError("color_map values need to be a Color object")

        self.name = name
        self.description = description
        self.metadata = metadata  # type: ignore

        super().__init__(color_map)

    @property
    def colors(self):
        return tuple(self.values())

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
    def from_dict(cls, map_dict: Dict[str, Any], color_space: Optional[ColorSpace] = None) -> Map:
        """create a new Map object from a Map dictionary

        Parameters
        ----------
        map_dict : Dict[str, Any]
            a Map dictionary
        color_space : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass). If None is supplied the default representation is used, by default None

        Returns
        -------
        Map
            A new Map object
        """

        if color_space is None:
            color_space = settings.default_color_space  # type: ignore

        ## init colors
        color_map = {name: BaseColor.from_dict(color, color_space) for name, color in map_dict["color_map"].items()}

        return cls(
            color_map=color_map,
            name=map_dict.get("name"),
            description=map_dict.get("description"),
            metadata=map_dict.get("metadata"),
        )

    def to_native(self):
        return {key: color.native for key, color in self.items()}

    def __setitem__(self, key, value):
        if not isinstance(value, BaseColor):
            raise TypeError("colors must by a Color or proper subclass")

        super().__setitem__(key, value)

    def __repr__(self) -> str:
        return f"Map{super().__repr__()}"

    def _repr_html_(self) -> str:
        html_string = '<table class="table">\n'

        html_string += "\n".join(
            [MAP_TABLE_ROW.format(text=key, css=color.css(), height=15, width=15) for key, color in self.items()]
        )
        html_string += "</table>"

        return html_string
