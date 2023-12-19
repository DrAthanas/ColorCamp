from typing import Sequence, Optional, Dict, Any, Union
from .color import WebColor
from ._color_metadata import ColorMetadata

DIV_TEMPLATE = """
<div style="
    width: {width}px; 
    height: {height}px; 
    background-color: {css}; 
    display: flex; 
    align-items: center; 
    justify-content: center;
">
</div>
"""


class Palette(ColorMetadata, tuple):
    def __init__(
        self,
        colors: Sequence[WebColor],
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Dict[str, Any] = {},
    ):
        self.name = name
        self.description = description
        self.metadata = metadata

        self.__current_index = 0
        super().__init__()

    @property
    def len(self):
        return len(self)

    def next(self):
        index = self.__current_index
        self.__current_index = (self.__current_index + 1) % len(self)

        return self[index]

    def __repr__(self) -> str:
        return f"Palette{super().__repr__()}"

    def _repr_html_(self):
        # TODO: Add name if needed
        html_string = "\n".join(
            [
                DIV_TEMPLATE.format(css=color.css(), height=60, width=60)
                for color in self
            ]
        )

        html_string = f'<div style="display: flex">{html_string}</div>'

        return html_string
