from __future__ import annotations
from typing import Dict, Any, Union, Optional
import colorsys
import math
from functools import cached_property
from pathlib import Path
import json
from itertools import zip_longest


from ._color_metadata import ColorMetadata
from .common.types import (
    GenericColorTuple,
    AnyGenericColorTuple,
    RGBColorTuple,
    AnyRGBColorTuple,
    Numeric,
)
from .conversions import (
    hex_to_rgb,
    rgb_to_hex,
)
from .common.validators import (
    FractionIntervalValidator,
    HueIntervalValidator,
    HexStringValidator,
    RGB256IntervalValidator,
)

# TODO
# * Validators
#   * from_dict ?
#   * load_json - pathing
# * __add__
# * fix slots on tuple subclass
# * Docstrings
# * css - inline vs constucted
# * Add other color base types (RGB_LINEAR, CMKY)
# * Other color space -> CIELAB

__all__ = ["Hex", "RGB", "HSL"]


# ? Move this inside method? Move to assets folder?
HTML_REPR_TEMPLATE = """<!DOCTYPE html>
<html>
<body>
    <div style="
        width: {width}px; 
        height: {height}px; 
        background-color: {css}; 
        display: flex; 
        align-items: center; 
        justify-content: center;
    ">
        <p style="
            text-align: center;
            color: white;
            font-size: 12px; /* Adjust the font size as needed */
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
        ">
            {text}
        </p>
    </div>
</body>
</html>
"""


class WebColor(ColorMetadata):
    """WebColor is a foundation for all other color formats. It uses the
    RGB color notation as its foundation as it is not bound to a colorspace.
    More importantly, it can represent any other color format, but not vice-versa.

    NOTE: This is not meant to be used within operational code
    """

    # pylint: disable=too-many-instance-attributes
    # There is a lot of functionality I want to keep here
    # pylint: disable=too-many-arguments
    # Users will not have to directly init this object

    _subclasses: Dict[str, WebColor] = {}

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
        self.rgb_linear = (red, green, blue)
        self._alpha = alpha
        self.name = name
        self.description = description
        self.metadata = metadata

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subclasses[cls.__name__] = cls

    @property
    def rgb_linear(self) -> AnyGenericColorTuple:
        if self.alpha is None:
            return self._rgb_linear
        return tuple((*self._rgb_linear, self.alpha))  # type: ignore

    @rgb_linear.setter
    def rgb_linear(self, value: GenericColorTuple):
        if hasattr(self, "_rgb_linear"):
            raise AttributeError("can't set attribute 'rgb_linear'")
        
        for channel, color in zip(['red','green','blue'], value):
            FractionIntervalValidator(channel).validate(color)
        self._rgb_linear = value

    @property
    def alpha(self) -> Union[float, None]:
        return self._alpha

    @alpha.setter
    def alpha(self, value: Union[float, None]):
        if hasattr(self, "_alpha"):
            raise AttributeError("can't set attribute 'alpha'")
        
        if value is not None:
            FractionIntervalValidator('alpha').validate(value)
        self._alpha = value
            
    def change_alpha(self, alpha: float):
        # If it's webclass it has a different signature
        if self.__class__.__name__ == "WebColor":
            return self.__class__(*self.rgb_linear[:3], alpha=alpha, **self.info())

        # types change based on subclasses - that's the point of this repo
        return self.__class__(self, alpha=alpha, **self.info())  # type: ignore

    ## Stored color types
    @cached_property
    def hsl(self) -> AnyGenericColorTuple:
        hue, lightness, saturation = colorsys.rgb_to_hls(*self.rgb_linear[:3])
        if self.alpha is None:
            return (hue*360, saturation, lightness)
        return (hue*360, saturation, lightness, self.alpha)

    @cached_property
    def rgb(self) -> AnyRGBColorTuple:
        rgb256 = list(map(lambda x: int(x * 255), self.rgb_linear[:3]))
        if self.alpha is None:
            return tuple(rgb256)  # type: ignore
        return (*rgb256, self.alpha)  # type: ignore

    @cached_property
    def hex(self) -> str:
        return rgb_to_hex(self.rgb)

    ## Conversion methods
    def to_color_type(self, color_type: str):
        if color_type is self.__class__.__name__:
            new_color: WebColor = self
        elif color_type in self._subclasses:
            new_color: WebColor = self._subclasses[color_type](  # type: ignore
                getattr(self, color_type.lower()),
                **self.info(),
                alpha=self.alpha,
            )
            # Bypass the setter to insure lrgb values are exact to avoid fp errors
            new_color._rgb_linear = self.rgb_linear[:3]  # pyline: ignore=W0212
        elif color_type == "WebColor":
            # ? Warning here?
            new_color = WebColor(*self.rgb_linear[:3], **self.info(), alpha=self.alpha)
        else:
            raise ValueError(
                f'Color type "{color_type}" is not in {list(self._subclasses.keys())}'
            )

        return new_color

    def to_hex(self):
        return self.to_color_type("Hex")

    def to_rgb(self):
        return self.to_color_type("RGB")

    def to_hsl(self):
        return self.to_color_type("HSL")

    ## Utility functions
    def css(self) -> str:
        # Needed some default - using rgb since it's inline with init
        return f"rgb{self.rgb}"

    def info(self) -> Dict[str, Any]:
        # DataClass?
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }

    def to_dict(self) -> Dict[str, Any]:
        # Add extra
        return {
            "red": self.rgb_linear[0],
            "green": self.rgb_linear[1],
            "blue": self.rgb_linear[2],
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "alpha": self.alpha,
            "color_formats":{
                ct:self.to_color_type(ct) for ct in self._subclasses.keys() 
            }
        }

    def dump_json(self, destination: Union[str, Path], overwrite=False) -> None:
        ## Validate path
        if isinstance(destination, (str, Path)):
            file_path = Path(destination)

        if file_path.exists() and not overwrite:
            # ? Check to see if it's writable?
            raise FileExistsError(f"file already exists for: {file_path}")

        with open(file_path, mode="w", encoding="utf-8") as fio:
            json.dump(self.to_dict(), fio, indent=4)

    @classmethod
    def from_dict(cls, color_dict: Dict[str, Any], color_type: Optional[str] = None):
        # ? any validation needed here?
        # default_type = color_dict.pop('default_type')
        if color_type is None:
            color_type = cls.__name__
            print(color_type)

        return WebColor(**color_dict).to_color_type(color_type)

    @classmethod
    def load_json(cls, source: Union[str, Path], color_type: Optional[str] = None):
        INITIALIZATION_ARGS = ['red', 'green', 'blue', 'name', 'description', 'metadata', 'alpha']
        if color_type is None:
            color_type = cls.__name__

        with open(source, "r", encoding="utf-8") as fio:
            color_dict : dict = json.load(fio)
            color_dict = {key:value for key, value in color_dict.items() if key in INITIALIZATION_ARGS}

        return WebColor.from_dict(color_dict, color_type)

    ## dunders
    # TODO: comparisons lt, gt
    def __eq__(self, color):
        if isinstance(color, WebColor):
            return all(
                map(
                    lambda p: math.isclose(p[0], p[1]),
                    zip_longest(self.rgb_linear, color.rgb_linear, fillvalue=1),
                )
            )
        elif isinstance(self, type(color)):
            # This converts the WebColor to the base type of the other object
            return type(color)(self) == color

        return False

    def __add__(self, color: WebColor) -> WebColor:
        if not isinstance(color, WebColor):
            raise TypeError('operator is only supported between two WebColors')
        # TODO: update for additive mix w/ alpha
        red, green, blue = map(
            lambda x: sum(x) / 2, zip(self.rgb_linear, color.rgb_linear)
        )

        return WebColor(red=red, green=green, blue=blue).to_color_type(
            self.__class__.__name__
        )

    def _repr_html_(self):
        text = "<br>".join(
            map(
                str,
                [
                    val
                    for val in [self.name, self.__class__.__name__, self.css()]
                    if val is not None
                ],
            )
        )

        return HTML_REPR_TEMPLATE.format(
            css=self.css(), width=100, height=100, text=text
        )


# NOTE: Alternative is 'from collections import UserString'
# # but then string methods return a Hex object, which I don't want
class Hex(WebColor, str):
    __slots__ = ("_hex", "_alpha", "_name", "_description", "_metadata")

    def __new__(cls, hex_str, *args, alpha=None, **kwargs):  # pylint: ignore=W0613
        if alpha is not None:
            hex_str = hex_str[:7] + f"{int(alpha*255):X}"
        return super().__new__(cls, hex_str)

    def __init__(
        self,
        hex_str: str,
        alpha: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.hex = hex_str
        red, green, blue = map(lambda v: v / 255, hex_to_rgb(hex_str))

        super().__init__(
            red=red,
            green=green,
            blue=blue,
            name=name,
            description=description,
            metadata=metadata,
            alpha=alpha,
        )

    @property
    def hex(self) -> str:
        return self._hex

    @hex.setter
    def hex(self, hex_string: str):
        if hasattr(self, "_hex"):
            raise AttributeError("can't set attribute 'hex'")

        HexStringValidator().validate(hex_string)
        self._hex = hex_string.upper()
            
    @property
    def red(self) -> int:
        return self.rgb[0]

    @property
    def green(self) -> int:
        return self.rgb[1]

    @property
    def blue(self) -> int:
        return self.rgb[2]

    def css(self) -> str:
        return str(self)

    ### Color manipulations
    # ? Can I do this cleaner with partials?
    def _change_rgb(self, red:Numeric, green:Numeric, blue:Numeric, keep_metadata: bool = False):
        metadata = self.info() if keep_metadata else {}
        return Hex(rgb_to_hex((red, green, blue)), alpha=self.alpha, **metadata)

    def change_red(self, red:Numeric, keep_metadata: bool = False):
        RGB256IntervalValidator('red').validate(red)
        _, green, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_green(self, green:Numeric, keep_metadata: bool = False):
        RGB256IntervalValidator('green').validate(green)
        red, _, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_blue(self, blue:Numeric, keep_metadata: bool = False):
        RGB256IntervalValidator('blue').validate(blue)
        red, green, _ = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def __str__(self) -> str:
        return self.upper()


class RGB(WebColor, tuple):
    # __slots__ = ('_rgb', '_alpha', '_name', '_description', '_metadata', )

    def __new__(cls, rgb, *args, alpha=None, **kwargs):
        if alpha is not None:
            rgb = tuple(list(rgb[:3]) + [alpha])
        return super().__new__(cls, rgb)

    def __init__(
        self,
        rgb: RGBColorTuple,
        alpha: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        
    ):
        red, green, blue = map(lambda v: v / 255, rgb[:3])
        self.rgb = rgb

        super().__init__(
            red=red,
            green=green,
            blue=blue,
            name=name,
            description=description,
            metadata=metadata,
            alpha=alpha,
        )

    @property
    def rgb(self) -> AnyRGBColorTuple:  # type: ignore
        if self.alpha is None:
            return self._rgb  # type: ignore
        return (*self._rgb, self.alpha)
    
    @rgb.setter
    def rgb(self, value:RGBColorTuple):
        if hasattr(self, "_rgb"):
            raise AttributeError("can't set attribute 'rgb'")
        for channel, color in zip(['red','green','blue'], value):
            RGB256IntervalValidator(channel).validate(color)
        self._rgb = value

    @property
    def red(self) -> int:
        return self.rgb[0]

    @property
    def green(self) -> int:
        return self.rgb[1]

    @property
    def blue(self) -> int:
        return self.rgb[2]

    def css(self) -> str:
        return super().css()

    ### Color manipulations
    def _change_rgb(self, red:Numeric, green:Numeric, blue:Numeric, keep_metadata: bool = False) -> RGB:
        metadata = self.info() if keep_metadata else {}
        return RGB((red, green, blue), alpha=self.alpha, **metadata)

    def change_red(self, red:Numeric, keep_metadata: bool = False) -> RGB:
        _, green, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_green(self, green:Numeric, keep_metadata: bool = False) -> RGB:
        red, _, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_blue(self, blue:Numeric, keep_metadata: bool = False) -> RGB:
        red, green, _ = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)


class HSL(WebColor, tuple):
    # __slots__ = ('_hsl', '_alpha', '_name', '_description', '_metadata')

    def __new__(cls, hsl, *args, alpha=None, **kwargs):
        if alpha is not None:
            hsl = tuple(list(hsl[:3]) + [alpha])

        return super().__new__(cls, hsl)

    def __init__(
        self,
        hsl: GenericColorTuple,
        alpha: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        # NOTE: order is funky b/c hsl <> hls
        red, green, blue = colorsys.hls_to_rgb(hsl[0] / 360, hsl[2], hsl[1])
        self.hsl = hsl

        super().__init__(
            red=red,
            green=green,
            blue=blue,
            name=name,
            description=description,
            metadata=metadata,
            alpha=alpha,
        )

    @property
    def hsl(self) -> AnyGenericColorTuple:
        if self.alpha is None:
            return self._hsl  # type: ignore
        return (*self._hsl, self.alpha)
    
    @hsl.setter
    def hsl(self, value:GenericColorTuple):
        if hasattr(self, "_hsl"):
            raise AttributeError("can't set attribute 'hsl'")
        HueIntervalValidator().validate(value[0])
        FractionIntervalValidator(value[1])
        FractionIntervalValidator(value[2])
        self._hsl = value

    @property
    def hue(self) -> float:
        return self.hsl[0]

    @property
    def saturation(self) -> float:
        return self.hsl[1]

    @property
    def lightness(self) -> float:
        return self.hsl[2]

    def css(self) -> str:
        return f"hsl({self.hue:.0f} {self.saturation:.0%} {self.lightness:.0%}{'' if self.alpha is None else ' / '+str(self.alpha)})"

    ### Color manipulations
    def _change_hsl(
        self, hue:Numeric, saturation:Numeric, lightness:Numeric, keep_metadata: bool = False
    ) -> HSL:
        metadata = self.info() if keep_metadata else {}
        return HSL((hue, saturation, lightness), alpha=self.alpha, **metadata)

    def change_hue(self, hue:Numeric, keep_metadata: bool = False) -> HSL:
        _, saturation, lightness = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)

    def change_saturation(self, saturation:Numeric, keep_metadata: bool = False) -> HSL:
        hue, _, lightness = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)

    def change_lightness(self, lightness:Numeric, keep_metadata: bool = False) -> HSL:
        hue, saturation, _ = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)
