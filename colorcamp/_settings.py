"""Apply package level settings"""

from typing import Sequence, Union
from pathlib import Path

from .common.types import ColorObject
from .common.validators import PathValidator, ColorTypeValidator

# TODO:
# * logging verbosity typing

PROJECT_PATHS = Path(__file__).parent.parent / "data"


class Settings:
    """Container for package 'colorcamp' universal settings"""

    def __init__(
        self,
        default_color_type: ColorObject = "Hex",
        camp_paths: Sequence[Union[Path, str]] = (PROJECT_PATHS,),
        verbosity=1,
    ):
        self.default_color_type = default_color_type
        self.camp_paths = camp_paths
        self.verbosity = verbosity

    @property
    def default_color_type(self) -> str:
        return self._default_color_type

    @default_color_type.setter
    def default_color_type(self, value: ColorObject):
        ColorTypeValidator().validate(value)
        self._default_color_type = value

    @property
    def camp_paths(self):
        return self._camp_paths

    @camp_paths.setter
    def camp_paths(self, value):
        for path in list(value):
            PathValidator().validate(path)
        self._camp_paths = value

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        # TODO: some validator
        self._verbosity = value


settings = Settings()
