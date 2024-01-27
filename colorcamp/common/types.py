from typing import Union, Tuple, Literal

Numeric = Union[int, float]

RGBColorTuple = Tuple[int, int, int]
RGBColorAlphaTuple = Tuple[int, int, int, float]
AnyRGBColorTuple = Union[RGBColorTuple, RGBColorAlphaTuple]

GenericColorTuple = Tuple[float, float, float]
GenericColorAlphaTuple = Tuple[float, float, float, float]
AnyGenericColorTuple = Union[GenericColorTuple, GenericColorAlphaTuple]

# Literal types to avoid circular imports
ColorSpace = Literal["Color", "Hex", "RGB", "HSL"]
ColorObject = Literal["Color", "Scale", "Palette", "Map"]
