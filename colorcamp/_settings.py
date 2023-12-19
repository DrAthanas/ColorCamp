"""Apply package level settings"""

from typing import Union, List, Literal, Union
from pathlib import Path

# TODO:
# * validators
# * logging verbosity typing

COLOR_TYPES =Union[Literal['Hex'], Literal['RGB'], Literal['HSL']]
PROJECT_PATHS = [Path(__file__).parent.parent / "data"]

class Settings:
    """Container for package 'colorcamp' universal settings"""
    def __init__(
        self,
        default_color_type: str = "Hex",
        camp_paths : List[Path] = PROJECT_PATHS,
        verbosity=1,
    ):
        self.default_color_type = default_color_type
        self.camp_paths = camp_paths
        self.verbosity = verbosity

    @property
    def default_color_type(self) -> str:
        return self._default_color_type
    
    @default_color_type.setter
    def default_color_type(self, value:COLOR_TYPES):
        # TODO: some validator
        self._default_color_type = value

    @property
    def camp_paths(self):
        return self._camp_paths
    
    @camp_paths.setter
    def camp_paths(self, value):
        # TODO: some validator
        self._camp_paths = value

    @property
    def verbosity(self):
        return self._verbosity
    
    @verbosity.setter
    def verbosity(self, value):
        # TODO: some validator
        self._verbosity = value