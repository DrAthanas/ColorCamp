from typing import List, AnyStr, Dict, Any, Union, Optional
import re
import colorsys
import math
from functools import cached_property
from pathlib import Path
import json

# TODO
# * Validators everywhere
# * Docstrings
# * Serialize method
# * css - inline vs constucted
# * Add other color base types (RGB_LINEAR, CMKY)
# * Other color space -> CIELAB

from .conversions import (
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_cmyk,
)

__all__ = ['Hex', 'RGB', 'HSL']

HEX_REGEX = re.compile(r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$")

#? Move this inside method? Move to assets folder?
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


class WebColor():
    """WebColor is a foundation for all other color formats. It uses the 
    RGB color notation as its foundation as it is not bound to a colorspace.
    More importantly, it can represent any other color format, but not vice-versa.

    NOTE: This is not meant to be used within operational code
    """

    _subclasses = {}

    def __init__(
            self,
            red:float,
            green:float,
            blue:float,
            name:str=None,
            description:str=None,
            metadata:Dict[str, Any]=None,
            alpha:Optional[float]=None,
            ):
        
        self.rgb_linear = (red, green, blue)
        self.name = name
        self.description = description
        self.metadata = metadata
        self._alpha = alpha


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subclasses[cls.__name__] = cls

    @property
    def rgb_linear(self):
        return self._rgb_linear
    
    @rgb_linear.setter
    def rgb_linear(self, value:tuple):
        if not hasattr(self, '_rgb_linear'):
            # TODO: Validation
            self._rgb_linear = value
        else:
            raise AttributeError("can't set attribute 'rgb_linear'")
        
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value:str):
        if not hasattr(self, '_name'):
            if isinstance(value, str) or value is None:
                self._name = value
            else:
                raise ValueError('expected a `str` for name')
        else:
            raise AttributeError("can't set attribute 'name'")

    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value:str):
        if not hasattr(self, '_description'):
            if isinstance(value, str) or value is None:
                self._description = value
            else:
                raise ValueError('expected a `str` for description')
        else:
            raise AttributeError("can't set attribute 'description'")
    
    @property
    def metadata(self) -> List[AnyStr]:
        return self._metadata
    
    @metadata.setter
    def metadata(self, value:List[AnyStr]):
        if not hasattr(self, '_metadata'):
            # TODO: Validate
            self._metadata = value
        else:
            raise AttributeError("can't set attribute 'metadata'")
        
    @property
    def alpha(self):
        return self._alpha
    
    @alpha.setter
    def alpha(self, value:float):
        if not hasattr(self, '_alpha'):
            if value is not None:
                if not isinstance(value, (float, int)) or (0 < value < 1):
                    raise ValueError("alpha must be between 0 and 1 inclusive")
            self._alpha = value
        else:
            raise AttributeError("can't set attribute 'alpha'")
        
    def change_alpha(self, alpha:float):
        # If it's webclass it has a different signature
        if self.__class__.__name__ == 'WebColor':
            return self.__class__(*self.rgb_linear, alpha=alpha, **self.info())
        
        return self.__class__(self, alpha=alpha, **self.info())

    ## Stored color types
    @cached_property
    def hsl(self):
        h, l, s = colorsys.rgb_to_hls(*self.rgb_linear)
        hsl_values = [h*360, s, l] + ([self.alpha] if self.alpha is not None else [])

        return tuple(hsl_values)

    @cached_property
    def rgb(self):
        rgb256 = list(map(lambda x: int(x*256), self.rgb_linear))
        rgb256 += [self.alpha] if self.alpha is not None else []
        return tuple(rgb256)

    @cached_property
    def hex(self):
        return rgb_to_hex(self.rgb)

    ## Conversion methods
    def to_color_type(self, color_type:str):
        if color_type is self.__class__.__name__:
            new_color = self
        elif color_type in self._subclasses:
            new_color : WebColor = self._subclasses[color_type](
                    getattr(self,color_type.lower()),
                    **self.info(),
                    alpha = self.alpha,
                )
            # Bypass the setter to insure lrgb values are exact to avoid fp errors
            new_color._rgb_linear = self.rgb_linear
        elif color_type == 'WebColor':
            #? Warning here?
            new_color = WebColor(*self.rgb_linear, **self.info(), alpha=self.alpha)
        else:
            raise ValueError(f'Color type "{color_type}" is not in {list(self._subclasses.keys())}')
        
        return new_color
    def to_hex(self):
        return self.to_color_type('Hex')

    def to_rgb(self):
        return self.to_color_type('RGB')

    def to_hsl(self):
        return self.to_color_type('HSL')

    ## Utility functions
    def css(self):
        # Place holder so that it works as baseclass
        UserWarning('css() method is ambiguous on WebColor. Convert to proper subtype')
        return self.hex
    
    def info(self) -> Dict[str, Any]:
        # DataClass?
        return {
            'name':self.name,
            'description':self.description,
            'metadata':self.metadata,
        }
    
    def to_dict(self):
        return {
            "red":self.rgb_linear[0],
            "green":self.rgb_linear[1],
            "blue":self.rgb_linear[2],
            "name":self.name,
            "description":self.description,
            "metadata":self.metadata,
            "alpha":self.alpha,
            #"default_type":self.__class__.__name__,
        }
    
    def dump_json(self, destination : Union[str, Path], overwrite = False)->None:
        ## Validate path
        if isinstance(destination, Union[str, Path]):
            file_path = Path(destination)
        
        if file_path.exists() and not overwrite:
            #? Check to see if it's writable?
            raise FileExistsError(f"file already exists for: {file_path}")

        with open(file_path, 'w') as fio:
            json.dump(self.to_dict(), fio, indent=4)

    @classmethod
    def from_dict(cls, color_dict:Dict[str,Any], color_type:Optional[str] = None):
        # ? any validation needed here?
        # default_type = color_dict.pop('default_type')
        if color_type is None:
            color_type = cls.__name__
            print(color_type)

        return WebColor(**color_dict).to_color_type(color_type)
    
    @classmethod
    def load_json(cls, source : Union[str, Path], color_type:str = None):
        #TODO: validate pathing?
        if color_type is None:
            color_type = cls.__name__

        with open(source, 'r') as fio:
            color_dict = json.load(fio)

        return WebColor.from_dict(color_dict, color_type)

    ## dunders
    # TODO: comparisons lt, gt
    def __eq__(self, color):
        # TODO: compare alpha channel
        if isinstance(color, WebColor):
            return all(map(lambda p: math.isclose(p[0], p[1]), zip(self.rgb_linear,color.rgb_linear)))
        
        return False
    
    def __add__(self, color):
        # TODO: update for additive mix w/ alpha
        r, g, b = map(lambda x: sum(x)/2, zip(self.rgb_linear, color.rgb_linear))

        return WebColor(red=r, green=g, blue=b).to_color_type(self.__class__.__name__)
    
    def _repr_html_(self):

        text = '<br>'.join(
            map(
                str, 
                [val for val in [self.name, self.__class__.__name__, self.css()] if val is not None]
            )
        )

        return HTML_REPR_TEMPLATE.format(
            css = self.css(),
            width = 100,
            height = 100,
            text = text 
        )


# NOTE: Alternative is 'from collections import UserString' 
# # but then string methods return a Hex object, which I don't want
class Hex(WebColor, str):
    __slots__ = ('_hex', '_alpha', '_name', '_description', '_metadata')

    def __new__(cls, hex, *args, alpha=None, **kwargs):
        if alpha is not None:
            hex = hex[:7] + f"{int(alpha*256):X}"
        return super().__new__(cls, hex)
    
    def __init__(
            self, 
            hex:str,
            name:str = None,
            description:str = None,
            metadata:List[str] = None,
            alpha:Optional[float] = None,
            ):
        
        self.hex = hex
        red, green, blue = map(lambda v: v/256, hex_to_rgb(hex))

        super().__init__(
            red = red,
            green = green,
            blue = blue,
            name = name,
            description = description,
            metadata = metadata,
            alpha = alpha
        )

    @property
    def hex(self) -> str:
        return self._hex
    
    @hex.setter
    def hex(self, hex:str):
        if not hasattr(self,'_hex'):
            if not HEX_REGEX.match(hex):
                raise ValueError(f"invalid hex code: {hex}")

            self._hex = hex.upper()
        else:
            raise AttributeError("can't set attribute 'hex'")

    @property
    def red(self) -> float:
        return self.rgb[0]
    
    @property
    def green(self) -> float:
        return self.rgb[1]

    @property
    def blue(self) -> float:
        return self.rgb[2]
    
    def css(self):
        return self.__str__()

    ### Color manipulations
    #? Can I do this cleaner with partials?
    def _change_rgb(self, red, green, blue, keep_metadata:bool=False):
        metadata = self.info() if keep_metadata else {}
        return Hex(rgb_to_hex(red, green, blue), alpha=self.alpha, **metadata)

    def change_red(self, red, keep_metadata : bool = False):
        _, green, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_green(self, green, keep_metadata : bool = False):
        red, _, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_blue(self, blue, keep_metadata : bool = False):
        red, green, _ = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)
    
    def __str__(self):
        return self.upper()
    

class RGB(WebColor, tuple):
    #__slots__ = ('_rgb', '_alpha', '_name', '_description', '_metadata', )

    def __new__(cls, rgb, *args, alpha=None, **kwargs):
        if alpha is not None:
            rgb = tuple(list(rgb[:3]) + [alpha])
        return super().__new__(cls, rgb)
    
    def __init__(
            self, 
            rgb:tuple,
            name:str = None,
            description:str = None,
            metadata:List[str] = None,
            alpha:Optional[float] = None,
            ):
        
        self.rgb = rgb
        red, green, blue = map(lambda v: v/256, rgb[:3])

        super().__init__(
            red = red,
            green = green,
            blue = blue,
            name = name,
            description = description,
            metadata = metadata,
            alpha = alpha
        )

    @property
    def rgb(self) -> tuple:
        return self._rgb
    
    @rgb.setter
    def rgb(self, rgb:tuple):
        if not hasattr(self,'_rgb'):
            #TODO: Validate
            self._rgb = rgb
        else:
            raise AttributeError("can't set attribute 'rgb'")

    @property
    def red(self) -> float:
        return self.rgb[0]
    
    @property
    def green(self) -> float:
        return self.rgb[1]

    @property
    def blue(self) -> float:
        return self.rgb[2]
    
    def css(self):
        return f"rgb{self}"

    ### Color manipulations
    #? Can I do this cleaner with partials?
    def _change_rgb(self, red, green, blue, keep_metadata:bool=False):
        metadata = self.info() if keep_metadata else {}
        return RGB((red, green, blue), alpha=self.alpha, **metadata)

    def change_red(self, red, keep_metadata : bool = False):
        _, green, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_green(self, green, keep_metadata : bool = False):
        red, _, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_blue(self, blue, keep_metadata : bool = False):
        red, green, _ = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)
    

class HSL(WebColor, tuple):
    #__slots__ = ('_hsl', '_alpha', '_name', '_description', '_metadata')

    def __new__(cls, hsl, *args, alpha=None, **kwargs):
        if alpha is not None:
            hsl = tuple(list(hsl[:3]) + [alpha])

        return super().__new__(cls, hsl)
    
    def __init__(
            self, 
            hsl:str,
            name:str = None,
            description:str = None,
            metadata:List[str] = None,
            alpha:float = 1,
            ):
        
        self.hsl = hsl
        red, green, blue = colorsys.hls_to_rgb(hsl[0]/360, hsl[2], hsl[1])

        super().__init__(
            red = red,
            green = green,
            blue = blue,
            name = name,
            description = description,
            metadata = metadata,
            alpha = alpha
        )

    @property
    def hsl(self) -> tuple:
        return self._hsl
    
    @hsl.setter
    def hsl(self, hsl:tuple):
        if not hasattr(self,'_hsl'):
            #TODO: Validate
            self._hsl = hsl
        else:
            raise AttributeError("can't set attribute 'hsl'")

    @property
    def hue(self) -> float:
        return self.hsl[0]
    
    @property
    def saturation(self) -> float:
        return self.hsl[1]

    @property
    def lightness(self) -> float:
        return self.hsl[2]
    
    def css(self): 
        return f"hsl({self.hue:.0f} {self.saturation:.0%} {self.lightness:.0%}{'' if self.alpha is None else ' / '+str(self.alpha)})"

    ### Color manipulations
    def _change_hsl(self, hue, saturation, lightness, keep_metadata:bool=False):
        metadata = self.info() if keep_metadata else {}
        return HSL((hue, saturation, lightness), alpha=self.alpha, **metadata)

    def change_hue(self, hue, keep_metadata : bool = False):
        _, saturation, lightness = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)

    def change_saturation(self, saturation, keep_metadata : bool = False):
        hue, _, lightness = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)

    def change_lightness(self, lightness, keep_metadata : bool = False):
        hue, saturation, _ = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)