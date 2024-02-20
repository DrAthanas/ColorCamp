"""Some basic functions all color collections have"""

from abc import abstractproperty
from typing import Dict

from colorcamp._color_metadata import MetaColor
from colorcamp.common.types import ColorSpace


class ColorGroup(MetaColor):
    _subclasses: Dict[str, type] = {}

    @abstractproperty
    def colors(self):
        NotImplementedError()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = cls.__name__
        cls._subclasses[name] = cls

    def __to_type(self, color_group_type, **kwargs):
        # TODO: Validate cg_type
        if color_group_type is self.__class__.__name__:
            new_group = self

        elif color_group_type == "Map":
            names = kwargs.get("names")
            colors = self.colors

            if names is None:
                names = [color.name for color in colors]

            if len(set(names)) != len(self.colors):
                raise ValueError("Uneven number of names and colors")

            color_map = {name: color for name, color in zip(names, colors)}
            new_group = self._subclasses[color_group_type](color_map, **self.info())

        else:
            new_group = self._subclasses[color_group_type](colors=self.colors, **kwargs, **self.info())

        return new_group

    def to_palette(self):
        return self.__to_type("Palette")

    def to_scale(self, stops=None):
        return self.__to_type("Scale", stops=stops)

    def to_map(self, names=None):
        return self.__to_type("Map", names=names)

    def to_color_type(self, color_type: ColorSpace):
        """convert current color object to a new representation

        Parameters
        ----------
        color_type : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass)

        Returns
        -------
        Color
            a new color object with the same metadata in a new color representation
        """

        return self.from_dict(self.to_dict(), color_type=color_type)
