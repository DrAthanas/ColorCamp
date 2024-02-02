"""Apply package level settings"""

from typing import Sequence, Union
from pathlib import Path

from .common.types import ColorSpace
from .common.validators import PathValidator, ColorTypeValidator

PROJECT_PATHS = Path(__file__).parent.parent / "data"


class Settings:
    """Container for package 'colorcamp' universal settings"""

    def __init__(
        self,
        default_color_type: ColorSpace = "Hex",
        camp_paths: Sequence[Union[Path, str]] = (PROJECT_PATHS,),
    ):
        self.default_color_type = default_color_type
        self.camp_paths = camp_paths

    @property
    def default_color_type(self) -> str:
        """Default color type that will used when loading new colors"""
        return self._default_color_type

    @default_color_type.setter
    def default_color_type(self, value: ColorSpace):
        ColorTypeValidator().validate(value)
        self._default_color_type = value

    @property
    def camp_paths(self):
        """Paths to search for camps in"""
        return self._camp_paths

    @camp_paths.setter
    def camp_paths(self, value):
        for path in list(value):
            PathValidator().validate(path)
        self._camp_paths = value


settings = Settings()
