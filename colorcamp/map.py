"""Mapping of hashes to Colors"""
from typing import Dict, Optional, Any, Hashable

from .color import WebColor
from ._color_metadata import ColorMetadata

DIV_TEMPLATE = """
<div style="
    float: left;
    width: {width}px; 
    height: {height}px; 
    background-color: {css};
    border: 1px solid black;
    display: flex; 
    align-items: center; 
    justify-content: center;
">
</div>
"""

class Map(ColorMetadata, dict):
    def __init__(
            self, 
            cmap:Dict[Hashable, WebColor],
            name: Optional[str] = None,
            description: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
        ):

        self.name = name
        self.description = description
        self.metadata = metadata

        super().__init__()

    def __repr__(self) -> str:
        return f"Map{super().__repr__()}"
    
    def _repr_html_(self) -> str:
        # TODO: Fix here
        html_string = "\n".join(
            [
                DIV_TEMPLATE.format(css=color.css(), height=60, width=60)
                for value, color in self.items()
            ]
        )

        html_string = f'<div style="display: flex">{html_string}</div>'

        return html_string
    
