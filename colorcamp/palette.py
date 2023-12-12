from typing import List, Sequence, Optional, Dict, Any, Union
from .color import WebColor

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


class Palette(tuple):
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

    @property
    def description(self) -> Union[str, None]:
        return self._description

    @description.setter
    def description(self, value: Union[str, None]):
        if not hasattr(self, "_description"):
            if isinstance(value, str) or value is None:
                self._description = value
            else:
                raise ValueError("expected a `str` for description")
        else:
            raise AttributeError("can't set attribute 'description'")

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._tags

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        if not hasattr(self, "_tags"):
            # TODO: Validate
            self._tags = value
        else:
            raise AttributeError("can't set attribute 'tags'")

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
