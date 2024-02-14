"""Camp organizes colors into frame work for projects"""

from typing import Any, Union, Optional, Dict, Sequence
from pathlib import Path
import json
from copy import copy

from ._settings import settings
from .color_objects._color_metadata import ColorInfo
from .common.types import ColorObject, ColorSpace
from .common.validators import PathValidator
from .color_objects.color_space import BaseColor
from .color_objects import Map, Scale, Palette

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


class Camp(ColorInfo):
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

    @staticmethod
    def __validate_serial_obj(current_dict: dict, file_path: Path, overwrite: bool) -> bool:
        """
        True -> no file or overwrite
        False -> file exists, but matches current
        """
        if file_path.exists() and not overwrite:
            with open(file_path, mode="r", encoding="utf-8") as fio:
                found = json.load(fio)

            if current_dict != found:
                raise FileExistsError(f"file already exists: {file_path}")

            return False
        return True

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

    @classmethod
    def load(
        cls,
        name: str,
        directory: Optional[Union[str, Path]] = None,
        color_type: Optional[ColorSpace] = None,
    ):
        """Load a saved camp

        Parameters
        ----------
        name : str
            Name of the saved camp. This must match a subdirectory within `directory`
        directory : Optional[Union[str, Path]], optional
            Absolute or relative path to where camp is saved, by default None
        color_type : ColorSpace, optional
            The new color representation (Color subclass). If None is supplied the default representation is used, by default None

        Returns
        -------
        Camp
            A collection of colors and color objects

        """
        if color_type is None:
            color_type = settings.default_color_type  # type: ignore

        # Search for matching directory in source locations
        if directory is None:
            # use config to find if name is in any sources
            camp_paths = list(settings.camp_paths)
            for camp_path in camp_paths:
                camp_dir = Path(camp_path) / name
                if camp_dir.exists():
                    break
            else:
                raise FileNotFoundError(f"No camp '{name}' found in {settings.camp_paths}")

        else:
            camp_dir = Path(directory) / name
            PathValidator().validate(camp_dir)

        with open(camp_dir / "camp_info.json", "r", encoding="utf-8") as fio:
            camp = cls(**json.load(fio))

        for sub_dir, klass in cls.__directory_map().items():
            search_dir: Path = camp_dir / sub_dir
            files = search_dir.glob("*.json") if search_dir.exists() else []
            for file in files:
                bucket: Bucket = getattr(camp, sub_dir)
                bucket.add(klass.load_json(file, color_type=color_type))

        return camp

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
        dest: Path = Path(directory) / self.name  # type: ignore
        dest.mkdir(exist_ok=True)

        info_path = dest / "camp_info.json"
        if self.__validate_serial_obj(self.info(), info_path, overwrite):
            with open(info_path, mode="w", encoding="utf-8") as fio:
                json.dump(self.info(), fio, indent=4)

        for sub_dir, _ in self.__directory_map().items():
            sub_dest_dir: Path = dest / sub_dir
            sub_dest_dir.mkdir(exist_ok=True)

            for name, color_object in getattr(self, sub_dir).to_dict().items():
                color_object_path = sub_dest_dir / f"{name}.json"

                if self.__validate_serial_obj(color_object.to_dict(), color_object_path, overwrite):
                    color_object.dump_json(color_object_path, overwrite=overwrite)
