"""Base Color Object"""

from __future__ import annotations

import math
from functools import cached_property
from itertools import zip_longest
from types import MethodType
from typing import Any, Dict, Optional, Union

from colorcamp._color_metadata import MetaColor
from colorcamp.common.types import (
    AnyGenericColorTuple,
    AnyRGBColorTuple,
    ColorSpace,
    GenericColorTuple,
)
from colorcamp.common.validators import FractionIntervalValidator
from colorcamp.conversions import rgb_to_hex, rgb_to_hsl
from colorcamp.static.html_templates import (
    HTML_NAME_TEMPLATE,
    HTML_REPR_TEMPLATE,
    MIN_HEIGHT,
    MIN_WIDTH,
)

__all__ = ["BaseColor"]


# pylint: disable=W0613
def make_to_color_space(self: BaseColor, name):
    """A function factory to make short cut methods to quickly convert color subtypes"""

    def changer(self):
        return self.to_color_space(name)

    return changer


# pylint: enable=W0613


class BaseColor(MetaColor):
    """BaseColor is a foundation for all other color formats. It uses the
    RGB color notation as its foundation as it is not bound to a colorspace.
    More importantly, it can represent any other color format, but not vice-versa.

    NOTE: This is not meant to be used within operational code
    """

    _subclasses: Dict[str, BaseColor] = {}

    # pylint: disable=too-many-arguments
    # Users will not have to directly init this object
    # pylint: disable=W0231
    def __init__(
        self,
        red: float,
        green: float,
        blue: float,
        alpha: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """A foundation for all other color representations

        Parameters
        ----------
        red : float
            fractional red color channel [0,1]
        green : float
            fractional green color channel [0,1]
        blue : float
            fractional blue color channel [0,1]
        alpha : Optional[float], optional
            alpha channel (opacity / transparency), by default None
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """

        self.fractional_rgb = (red, green, blue)
        self.alpha = alpha
        self.name = name
        self.description = description
        self.metadata = metadata  # type: ignore

        # Dynamically add functions based on subclasses
        for subclass in self._subclasses:
            env_setter = make_to_color_space(self, subclass)

            method = MethodType(env_setter, self)
            setattr(self, f"to_{subclass.lower()}", method)

    # pylint: enable=too-many-arguments
    # pylint: enable=W0231

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = cls.__name__
        cls._subclasses[name] = cls

    @property
    def fractional_rgb(self) -> AnyGenericColorTuple:
        """fractional RGB [0,1]"""

        if self.alpha is None:
            return self._fractional_rgb
        return tuple((*self._fractional_rgb, self.alpha))  # type: ignore

    @fractional_rgb.setter
    def fractional_rgb(self, value: GenericColorTuple):
        if hasattr(self, "_fractional_rgb"):
            raise AttributeError("can't set attribute 'fractional_rgb'")

        for channel, color in zip(["red", "green", "blue"], value):
            FractionIntervalValidator(channel).validate(color)
        self._fractional_rgb = value

    @property
    def alpha(self) -> Union[float, None]:
        """alpha channel [0,1]"""
        return self._alpha

    @alpha.setter
    def alpha(self, value: Union[float, None]):
        if hasattr(self, "_alpha"):
            raise AttributeError("can't set attribute 'alpha'")

        if value is not None:
            FractionIntervalValidator("alpha").validate(value)
        self._alpha = value

    def change_alpha(self, alpha: float):
        """change the alpha value and return a new color object

        Parameters
        ----------
        alpha : float
            the new alpha value [0,1]

        Returns
        -------
        Color
            a new color object with the same metadata and of same color type
        """

        # If it's base color it has a different signature
        if self.__class__.__name__ == "BaseColor":
            return self.__class__(*self.fractional_rgb[:3], alpha=alpha, **self.info())

        # types change based on subclasses - that's the point of this repo
        return self.__class__(self, alpha=alpha, **self.info())  # type: ignore

    ## Stored color types
    @cached_property
    def hsl(self) -> AnyGenericColorTuple:
        """represents a color in HSL (Hue, Saturation, Lightness) color space"""

        return rgb_to_hsl(self.fractional_rgb)

    @cached_property
    def rgb(self) -> AnyRGBColorTuple:
        """represents a color in RGB (Red, Green, Blue) color space"""

        rgb256 = list(map(lambda x: round(x * 255), self.fractional_rgb[:3]))
        if self.alpha is None:
            return tuple(rgb256)  # type: ignore
        return (*rgb256, self.alpha)  # type: ignore

    @cached_property
    def hex(self) -> str:
        """represents a color in hexadecimal format"""

        return rgb_to_hex(self.rgb)

    @property
    def native(self):
        """Get the native color representation stripped of all BaseColor extensions

        Returns
        -------
        Union[str, tuple]
            The base type representation of the color
        """
        return getattr(self, self.__get_default_rep())

    ## Conversion methods
    def to_color_space(self, color_space: ColorSpace):
        """convert current color object to a new representation

        Parameters
        ----------
        color_space : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass)

        Returns
        -------
        Color
            a new color object with the same metadata in a new color representation
        """

        if color_space is self.__class__.__name__:
            new_color: BaseColor = self
        elif color_space in self._subclasses:
            new_color: BaseColor = self._subclasses[color_space](  # type: ignore
                getattr(self, color_space.lower()),
                **self.info(),
                alpha=self.alpha,
            )
            # Bypass the setter to insure frgb values are exact to avoid fp errors
            new_color._fractional_rgb = self.fractional_rgb[:3]  # pylint: disable=W0212
        elif color_space == "BaseColor":
            new_color = BaseColor(*self.fractional_rgb[:3], **self.info(), alpha=self.alpha)
        else:
            raise ValueError(f'Color type "{color_space}" is not in {list(self._subclasses.keys())}')

        return new_color

    ## Utility functions
    def css(self) -> str:
        """generate inline css for a color

        Returns
        -------
        str
            inline css for color representation
        """

        # Needed some default - using rgb since it's inline with init
        return f"rgb{self.rgb}"

    def to_dict(self) -> Dict[str, Any]:
        """create a dictionary of all color attributes

        Returns
        -------
        Dict[str, Any]
            dictionary with the underlying color representation
        """

        return {
            "type": self.__class__.__name__,
            **self.info(),
            "value": self.native,
            # "red": self.fractional_rgb[0],
            # "green": self.fractional_rgb[1],
            # "blue": self.fractional_rgb[2],
            # "alpha": self.alpha,
        }

    @classmethod
    def from_dict(cls, color_dict: Dict[str, Any], color_space: Optional[ColorSpace] = None) -> BaseColor:
        """Create a new color object from a color dictionary

        Parameters
        ----------
        color_dict : Dict[str, Any]
            A Color dictionary
        color_space : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            The new color representation (Color subclass). If None is supplied the current representation is used, by default None

        Returns
        -------
        Color
            A new Color object
        """

        init_args = {
            "name",
            "description",
            "metadata",
            "alpha",
        }

        if color_space is None:
            color_space = cls.__name__  # type: ignore

        value = color_dict.pop("value")
        _type = color_dict.pop("type")
        init_dict = {key: value for key, value in color_dict.items() if key in init_args}
        if _type == "BaseColor":
            new_color = cls(*value, **init_dict)
        else:
            new_color = cls._subclasses[_type](value, **init_dict)  # type: ignore

        return new_color.to_color_space(color_space)  # type: ignore

    def equivalence(self, color: Any) -> bool:
        """Check if two colors are essentially the same. This allows for comparisons
        across color spaces and some reasonable rounding errors.

        Parameters
        ----------
        color : Any
            The other color

        Returns
        -------
        bool
            The equivalence of two colors
        """

        if isinstance(color, BaseColor):
            # Determine relative precision
            tolerances = {
                "Hex": 1 / (255 * 2),
                "RGB": 1 / (255 * 2),
            }

            return all(
                map(
                    lambda p: math.isclose(
                        p[0],
                        p[1],
                        abs_tol=tolerances.get(self.__class__.__name__, 1e-9),
                    ),
                    zip_longest(self.fractional_rgb, color.fractional_rgb, fillvalue=1),
                )
            )

        if isinstance(self, type(color)):
            # This converts the Color to the base type of the other object
            return type(color)(self) == color

        return False

    ## dunders
    def __eq__(self, color):
        if isinstance(color, BaseColor):
            return self.native == color.native

        # This allows for directly comparing strings / tuples
        return self.native == color

    def __add__(self, color: BaseColor) -> BaseColor:
        if not isinstance(color, BaseColor):
            raise TypeError("addition operator is only supported between two Color objects")

        red, green, blue = map(lambda x: sum(x) / 2, zip(self.fractional_rgb[:3], color.fractional_rgb[:3]))

        return BaseColor(red=red, green=green, blue=blue).to_color_space(self.__class__.__name__)  # type: ignore

    def __hash__(self):
        return hash(self.native)

    def _repr_html_(self):
        name = "" if self.name is None else HTML_NAME_TEMPLATE.format(name=self.name)
        css = self.css()

        return HTML_REPR_TEMPLATE.format(
            name=name,
            color=f"background-color: {css};",
            text=css,
            width=MIN_WIDTH,
            height=MIN_HEIGHT,
        )

    def __get_default_rep(self) -> str:
        """Get the default representation of this color object

        Returns
        -------
        str
            lowercase name of color representation
        """

        rep = self.__class__.__name__.lower()
        rep = "fractional_rgb" if rep == "basecolor" else rep

        return rep
