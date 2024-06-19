"""Apply package level settings"""

from pathlib import Path
from typing import Sequence, Union

from .common.types import ColorSpace
from .common.validators import ColorTypeValidator, PathValidator

__all__ = ["settings"]

PROJECT_PATHS = (
    Path(__file__).parent / "data",
    Path.cwd(),
)


class Settings:
    """Container for package 'colorcamp' universal settings"""

    def __init__(
        self,
        default_color_space: ColorSpace = "Hex",
        camp_paths: Sequence[Union[Path, str]] = PROJECT_PATHS,
    ):
        self.default_color_space = default_color_space
        self.camp_paths = camp_paths
        self._max_precision = 6

    @property
    def default_color_space(self) -> str:
        """Default color type that will used when loading new colors"""
        return self._default_color_space

    @default_color_space.setter
    def default_color_space(self, value: ColorSpace):
        ColorTypeValidator().validate(value)
        self._default_color_space = value

    @property
    def camp_paths(self):
        """Paths to search for camps in"""
        return self._camp_paths

    @camp_paths.setter
    def camp_paths(self, value):
        for path in list(value):
            PathValidator().validate(path)
        self._camp_paths = value

    @property
    def max_precision(self):
        """Maximum number of decimal places to use for precision calculations"""
        return self._max_precision

    @max_precision.setter
    def max_precision(self, value: int):
        # TODO: add validator
        self._max_precision = value


settings = Settings()
