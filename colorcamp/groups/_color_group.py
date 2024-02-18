"""Some basic functions all color collections have"""

from abc import abstractproperty
from typing import Dict

from colorcamp._color_metadata import MetaColor


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
        # TODO: Validate co_type
        if color_group_type is self.__class__.__name__:
            new_group = self

        elif color_group_type == "Map":
            names = kwargs.get("names")
            colors = self.colors

            if names is None:
                names = [color.name for color in colors]

            if len(set(names)) != len(self.colors):
                raise RuntimeError()

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
