"""Custom types for ColorCamp package"""

from typing import Literal, Tuple, Union

Numeric = Union[int, float]

RGBColorTuple = Tuple[int, int, int]
RGBColorAlphaTuple = Tuple[int, int, int, float]
# Doesn't like this name?
# pylint: disable=C0103
AnyRGBColorTuple = Union[RGBColorTuple, RGBColorAlphaTuple]
# pylint: enable=C0103

GenericColorTuple = Tuple[float, float, float]
GenericColorAlphaTuple = Tuple[float, float, float, float]
AnyGenericColorTuple = Union[GenericColorTuple, GenericColorAlphaTuple]

# Literal types to avoid circular imports
ColorSpace = Literal["BaseColor", "Hex", "RGB", "HSL"]
ColorObject = Literal["BaseColor", "Scale", "Palette", "Map"]
