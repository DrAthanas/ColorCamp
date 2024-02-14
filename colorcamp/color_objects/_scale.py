"""Linear gradients of Colors"""

from __future__ import annotations
from typing import Sequence, Optional, Dict, Any


from colorcamp._settings import settings
from colorcamp.common.types import ColorSpace, Numeric
from colorcamp.common.validators import FractionIntervalValidator
from .color_space import BaseColor
from ._color_metadata import MetaColor

DIV_TEMPLATE = """
<div style="
    width: {width}px; 
    height: {height}px; 
    background-image: linear-gradient(to right, {grad}); 
    display: flex; 
    align-items: center; 
    justify-content: center;
">
</div>
"""


class Scale(MetaColor, tuple):
    """An object to represent continuous color Scales"""

    # pylint: disable=W0613
    def __new__(cls, colors, *args, **kwargs):
        if not all((isinstance(color, BaseColor) for color in colors)):
            raise TypeError("colors must by a Color or proper subclass")
        return super().__new__(cls, colors)

    def __init__(
        self,
        colors: Sequence[BaseColor],
        stops: Optional[Sequence[Numeric]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Color Scales are used for continuous data and color gradients

        Parameters
        ----------
        colors : Sequence[BaseColor]
            A sequence of Colors
        stops : Optional[Sequence[Numeric]], optional
            Relative numeric stops which correspond to color transitions. must be the same length as `colors` and sorted ascending, by default None
        name : Optional[str], optional
            Descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            Short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            Unstructured metadata used for querying and additional context, by default None
        """

        super().__init__(
            colors,
            name=name,
            description=description,
            metadata=metadata,
        )
        # Set stops after super().init to set up colors attr
        self.stops = stops

    @property
    def stops(self):
        """Color stops in the Scale"""

        return self._stops

    @stops.setter
    def stops(self, values):
        if values is None:
            n_colors = len(self.colors)
            values = [i / (n_colors - 1) for i in range(n_colors - 1)] + [1]
        elif len(values) != len(self.colors) or sorted(values) != list(values):
            raise ValueError("stops must be sorted in ascending order and be of the same length as colors")

        _ = (FractionIntervalValidator().validate(val) for val in values)

        self._stops = values

    @property
    def colors(self):
        """Sequence of Colors"""

        return tuple(self)

    def to_dict(self):
        """Create a dictionary of all Scale attributes

        Returns
        -------
        Dict[str, Any]
            Dictionary with the underlying Scale representation
        """

        return {
            "type": "Scale",
            **self.info(),
            "colors": [color.to_dict() for color in self],
            "stops": self.stops,
        }

    @classmethod
    def from_dict(cls, scale_dict: Dict[str, Any], color_type: Optional[ColorSpace] = None) -> Scale:
        """Create a new Scale object from a Scale dictionary

        Parameters
        ----------
        scale_dict : Dict[str, Any]
            A Scale dictionary
        color_type : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            The new color representation (Color subclass). If None is supplied the default representation is used, by default None

        Returns
        -------
        Scale
            A new Scale object
        """

        if color_type is None:
            color_type = settings.default_color_type  # type: ignore

        ## init colors
        colors = [BaseColor.from_dict(color, color_type) for color in scale_dict["colors"]]

        return cls(
            colors=colors,
            stops=scale_dict.get("stops"),
            name=scale_dict.get("name"),
            description=scale_dict.get("description"),
            metadata=scale_dict.get("metadata"),
        )

    def __repr__(self):
        return f"Scale{tuple(zip(self, self.stops))}"

    def _repr_html_(self):
        grad = ", ".join([f"{color.css()} {stop:.0%}" for color, stop in zip(self, self.stops)])
        html_string = DIV_TEMPLATE.format(grad=grad, height=60, width=max(60 * len(self), 180))

        return html_string
