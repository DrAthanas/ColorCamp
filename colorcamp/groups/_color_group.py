"""Some basic functions all color collections have"""

from __future__ import annotations

from abc import abstractmethod
from typing import Dict, Hashable, Optional, Sequence, Tuple

from colorcamp._color_metadata import MetaColor
from colorcamp.color_space import BaseColor
from colorcamp.common.types import ColorSpace, Numeric
from colorcamp.common.validators import ColorGroupValidator


class ColorGroup(MetaColor):
    """Base class for any group of colors"""

    _subclasses: Dict[str, type] = {}

    @property
    @abstractmethod
    def colors(self) -> Tuple[BaseColor]:
        """Sequence of colors"""
        return

    @abstractmethod
    def to_native(self):
        """Return the native type of the color group (tuple | dict)"""

        return

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = cls.__name__
        cls._subclasses[name] = cls

    def __to_type(self, color_group_type: str, **kwargs):
        ColorGroupValidator().validate(color_group_type)

        if color_group_type is self.__class__.__name__:
            new_group = self

        elif color_group_type == "Map":
            names = kwargs.get("names")
            colors = self.colors

            if names is None:
                names = [color.name for color in colors]

            if len(set(names)) != len(self.colors):
                raise ValueError("Uneven number of names and colors")

            color_map = dict(zip(names, colors))
            new_group = self._subclasses[color_group_type](color_map, **self.info())

        else:
            new_group = self._subclasses[color_group_type](colors=self.colors, **kwargs, **self.info())

        return new_group

    def to_palette(self) -> "Palette":  # type: ignore
        """Convert the current color group into a color palette object

        Returns
        -------
        Palette
        """
        return self.__to_type("Palette")

    def to_scale(self, stops: Optional[Sequence[Numeric]] = None) -> "Scale":  # type: ignore
        """Convert the current color group into a color scale object

        Parameters
        ----------
        stops : Optional[Sequence[Numeric]], optional
            Relative numeric stops which correspond to color transitions. must be the same length as `colors` and sorted ascending, by default None

        Returns
        -------
        Scale
        """
        return self.__to_type("Scale", stops=stops)

    def to_map(self, names: Optional[Sequence[Hashable]] = None) -> "Map":  # type: ignore
        """Convert the current color group into a color scale object

        Parameters
        ----------
        names : Sequence[Hashable], optional
            Key values to be used in the color map. If not are provided color names are attempted, by default None

        Returns
        -------
        Map
        """
        return self.__to_type("Map", names=names)

    def to_color_space(self, color_space: ColorSpace) -> ColorGroup:
        """Convert current color object to a new representation

        Parameters
        ----------
        color_space : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass)

        Returns
        -------
        Color
            a new color object with the same metadata in a new color representation
        """

        return self.from_dict(self.to_dict(), color_space=color_space)
