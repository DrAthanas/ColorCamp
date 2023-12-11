from typing import Union, Tuple

RGBColorTuple = Tuple[int, int, int]
RGBColorAlphaTuple = Tuple[int, int, int, float]
AnyRGBColorTuple = Union[RGBColorTuple, RGBColorAlphaTuple]

GenericColorTuple = Tuple[float, float, float]
GenericColorAlphaTuple = Tuple[float, float, float, float]
AnyGenericColorTuple = Union[GenericColorTuple, GenericColorAlphaTuple]