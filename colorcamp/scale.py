from typing import List, Iterable, AnyStr, Union
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


class Scale(tuple):
    def __init__(
        self,
        colors: Iterable[WebColor],
        stops: Iterable[Union[float, int]] = None,
        name: str = None,
        description: str = None,
        tags: List[str] = None,
    ):
        self.name = name
        self.description = description
        self.tags = tags

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

        r1, g1, b1 = map(lambda x: x * relative_value, color1.rgb)
        r2, g2, b2 = map(lambda x: x * relative_value, color2.rgb)

        # TODO: Return type!
        return WebColor(r1 + r2, g1 + g2, b1 + b2)

    @property
    def len(self):
        return self.__len__()

    def __repr__(self):
        # TODO: Fix this
        return f"Scale{super().__repr__()}"

    def _repr_html_(self):
        grad = ", ".join(
            [f"{color.hex} {stop:.0%}" for color, stop in zip(self, self.stops)]
        )
        html_string = DIV_TEMPLATE.format(
            grad=grad, height=60, width=max(60 * self.len, 180)
        )

        return html_string
