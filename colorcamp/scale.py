from typing import Sequence, Union, Optional, Dict, Any, Tuple
from .color import WebColor

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


class Scale(Tuple[WebColor]):
    def __init__(
        self,
        colors: Sequence[WebColor],
        stops: Optional[Sequence[Union[float, int]]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Dict[str, Any] = {},
    ):
        self.name = name
        self.description = description
        self.metadata = metadata

        if stops is None:
            n_colors = len(colors)
            stops = [i / (n_colors - 1) for i in range(n_colors - 1)] + [1]
        elif len(stops) != len(colors) or sorted(stops) != stops:
            # What type of validation do I want here. e.g. Should it always be between 0 and 1?!?
            raise ValueError()

        self.stops = stops

        super().__init__()

    def get_color(
        self, value, min_val: Union[float, int] = 0, max_val: Union[float, int] = 1
    ):
        # TODO: Vectorize this
        # Finds color that falls within scale
        norm_value = (value - min_val) / (max_val - min_val)
        # Find which two colors this sits between
        max_idx = sum([stop < norm_value for stop in self.stops])

        color1, color2 = self[max_idx - 1], self[max_idx]
        relative_value = (norm_value - self.stops[max_idx - 1]) / (
            self.stops[max_idx] - self.stops[max_idx - 1]
        )

        red_1, green_1, blue_1 = map(lambda x: x * relative_value, color1.rgb)
        red_2, green_2, blue_2 = map(lambda x: x * relative_value, color2.rgb)

        # TODO: Return type!
        return WebColor(
            red=red_1 + red_2, green=green_1 + green_2, blue=blue_1 + blue_2
        )

    @property
    def len(self):
        return len(self)

    @property
    def name(self) -> Union[str, None]:
        return self._name

    @name.setter
    def name(self, value: Union[str, None]):
        if not hasattr(self, "_name"):
            if isinstance(value, str) or value is None:
                self._name = value
            else:
                raise ValueError("expected a `str` for name")
        else:
            raise AttributeError("can't set attribute 'name'")

    def __repr__(self):
        return f"Scale{tuple(zip(super().__repr__(), self.stops))}"

    def _repr_html_(self):
        grad = ", ".join(
            [f"{color.hex} {stop:.0%}" for color, stop in zip(self, self.stops)]
        )
        html_string = DIV_TEMPLATE.format(
            grad=grad, height=60, width=max(60 * self.len, 180)
        )

        return html_string
