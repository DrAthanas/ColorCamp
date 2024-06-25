"""Camp organizes colors into frame work for projects"""

from __future__ import annotations

import json
from copy import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from ._color_metadata import MetaColor
from ._settings import settings
from .color_space import BaseColor
from .common.types import ColorObject, ColorSpace
from .common.validators import PathValidator
from .groups import Map, Palette, Scale

__all__ = ["Camp"]

ColorObjectType = Union[type[BaseColor], type[Scale], type[Palette], type[Map]]


class Bucket:
    """A bucket for Color Objects"""

    def __init__(self, bucket_type: ColorObjectType):
        """A bucket for Color objects

        Parameters
        ----------
        bucket_type : ColorObjectType
            One of the key Color objects: Color, Scale, Palette, Map
        """

        self._bucket_type = bucket_type

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "_bucket_type":
            # ? Validate
            pass
        elif not isinstance(__value, self._bucket_type):
            raise TypeError(f"Colors must be of {self._bucket_type.__name__}")
        elif __value.name != __name:
            raise AttributeError(f"Names do not match: {__value.name}, {__name}")
        super().__setattr__(__name, __value)

    def __getitem__(self, value):
        return self.__dict__[value]

    def add(self, item: ColorObject):
        """
        Add an item of matching type to the bucket.

        Parameters
        ----------
        item : Union[Color, Scale, Palette, Map]
            Item to add to the

        """

        if (name := item.name) is None:  # type: ignore
            raise AttributeError(f"Objects need to have a name to be added to a Camp {self.__class__.__name__} Bucket")
        if hasattr(self, name):
            raise ValueError(f"name '{name}' is already in use")
        setattr(self, name, item)

    def remove(self, name: str):
        """Remove item from the bucket by name

        Parameters
        ----------
        name : str
            name of the item

        """
        if not hasattr(self, name):
            raise KeyError(f"name '{name} is not in bucket")
        delattr(self, name)

    def to_dict(self) -> Dict[str, ColorSpace]:
        """Return the bucket as a dictionary

        Returns
        -------
        ColorSpace
            Color object of the bucket type
        """

        bucket_dict = copy(self.__dict__)
        bucket_dict.pop("_bucket_type")

        return bucket_dict

    @property
    def names(self):
        """Names of color objects in the bucket"""

        return list(self.to_dict().keys())

    def __repr__(self):
        bucket_type = self._bucket_type.__name__
        if bucket_type == "BaseColor":
            bucket_type = "Color"
        return f"{bucket_type}s{self.names}"


class Camp(MetaColor):
    """A camp of colors!"""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """A collection of colors and color objects. A Camp of Colors!

        Parameters
        ----------
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """

        super().__init__(
            name=name,
            description=description,
            metadata=metadata,
        )

        self._colors = Bucket(bucket_type=BaseColor)
        self._scales = Bucket(bucket_type=Scale)
        self._palettes = Bucket(bucket_type=Palette)
        self._maps = Bucket(bucket_type=Map)

    @property
    def colors(self):
        """Named camp colors"""
        return self._colors

    @property
    def scales(self):
        """Named camp scales"""
        return self._scales

    @property
    def palettes(self):
        """Named camp palettes"""
        return self._palettes

    @property
    def maps(self):
        """Named camp maps"""
        return self._maps

    @classmethod
    def __directory_map(cls) -> Dict[str, ColorObjectType]:
        dir_map: Dict[str, ColorObjectType] = {
            "colors": BaseColor,
            "scales": Scale,
            "palettes": Palette,
            "maps": Map,
        }

        return dir_map

    def add_objects(self, color_objects: Sequence[ColorObject], exists_ok=False):
        """Add any number of color objects to the Camp

        Parameters
        ----------
        color_objects : Sequence[ColorObject]
            A sequence of color objects
        exists_ok : bool, optional
            Ignore ValueErrors if conflicting names exist, by default False
        """

        map_directory = {klass.__name__: key for key, klass in self.__directory_map().items()}

        for color_object in list(color_objects):
            if isinstance(color_object, BaseColor):
                co_type = "BaseColor"
            else:
                co_type = color_object.__class__.__name__

            bucket: Bucket = getattr(self, map_directory[co_type])
            try:
                bucket.add(color_object)
            except ValueError as value_error:
                if not exists_ok:
                    raise value_error

    @staticmethod
    def find(directory: Optional[Union[str, Path]] = None) -> Dict[str, List[str]]:
        """Find all valid camps in default directories or a provided one

        Parameters
        ----------
        directory : Optional[Union[str, Path]], optional
            An optional search directory, by default None

        Returns
        -------
        Dict[str, List[str]]
            All found camps within input directories. They key is the root director, and the key is a list of camp names found

        """
        found_camps = {}

        if directory is None:
            camp_paths = [Path(cpath) for cpath in settings.camp_paths]
        else:
            PathValidator().validate(directory)
            camp_paths = [Path(directory)]

        def only_valid_camp(check_paths: List[Path]):
            for cpath in check_paths:
                with open(cpath, "r", encoding="utf-8") as fio:
                    camp_dict: dict = json.load(fio)

                if camp_dict.get("type", None) == "Camp":
                    yield cpath.stem

        for camp_path in camp_paths:
            found_camps[str(camp_path)] = list(only_valid_camp(camp_path.glob("*.json")))  # type: ignore

        return found_camps

    def to_dict(self):
        """Create a dictionary of all Camp attributes

        Returns
        -------
        Dict[str, Any]
            dictionary with the underlying Camp representation
        """

        return {
            "type": "Camp",
            **self.info(),
            "colors": [color.to_dict() for color in self.colors.to_dict().values()],
            "palettes": [palette.to_dict() for palette in self.palettes.to_dict().values()],
            "scales": [scale.to_dict() for scale in self.scales.to_dict().values()],
            "maps": [_map.to_dict() for _map in self.maps.to_dict().values()],
        }

    @classmethod
    def from_dict(cls, camp_dict: Dict[str, Any], color_space: Optional[ColorSpace] = None) -> Camp:
        """create a new Camp object from a Camp dictionary

        Parameters
        ----------
        camp_dict : Dict[str, Any]
            a Camp dictionary
        color_space : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass). If None is supplied the default representation is used, by default None

        Returns
        -------
        Camp
            A new Camp object
        """

        if color_space is None:
            color_space = settings.default_color_space  # type: ignore

        color_objects = (
            [BaseColor.from_dict(color, color_space) for color in camp_dict.get("colors", [])]
            + [Palette.from_dict(palette, color_space) for palette in camp_dict.get("palettes", [])]
            + [Scale.from_dict(scale, color_space) for scale in camp_dict.get("scales", [])]
            + [Map.from_dict(_map, color_space) for _map in camp_dict.get("maps", [])]
        )

        new_camp: Camp = cls(
            name=camp_dict["name"],
            description=camp_dict.get("description"),
            metadata=camp_dict.get("metadata"),
        )

        new_camp.add_objects(color_objects=color_objects)

        return new_camp

    @classmethod
    def load(
        cls,
        name: str,
        directory: Optional[Union[str, Path]] = None,
        color_space: Optional[ColorSpace] = None,
    ):
        """Load a saved camp

        Parameters
        ----------
        name : str
            Name of the saved camp. This must match a subdirectory within `directory`
        directory : Optional[Union[str, Path]], optional
            Absolute or relative path to where camp is saved, by default None
        color_space : ColorSpace, optional
            The new color representation (Color subclass). If None is supplied the default representation is used, by default None

        Returns
        -------
        Camp
            A collection of colors and color objects

        """
        if color_space is None:
            color_space = settings.default_color_space  # type: ignore

        # Search for matching directory in source locations
        if directory is None:
            # use config to find if name is in any sources
            for camp_path in list(settings.camp_paths):
                camp_dir = Path(camp_path) / f"{name}.json"
                if camp_dir.exists():
                    break
            else:
                raise FileNotFoundError(f"No camp '{name}' found in {settings.camp_paths}")

        else:
            camp_dir = Path(directory) / f"{name}.json"
            PathValidator().validate(camp_dir)

        return Camp.load_json(camp_dir)

    def save(self, directory: Union[str, Path], overwrite=False):
        """Save a camp

        Parameters
        ----------
        directory : Union[str, Path]
            Absolute or relative path to where camp is saved
        overwrite : bool, optional
            Overwrite files, by default False
        """

        PathValidator().validate(directory)
        dest: Path = Path(directory) / f"{self.name}.json"  # type: ignore

        self.dump_json(dest, overwrite)
