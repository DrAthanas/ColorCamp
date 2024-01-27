"""Camp organizes colors into frame work for projects"""

from typing import Any, Union, Optional, Dict, List
from pathlib import Path
import re
import json

from ._settings import settings
from ._color_metadata import ColorInfo
from .common.types import ColorObject, ColorSpace
from .common.validators import PathValidator
from .color import BaseColor
from .scale import Scale
from .palette import Palette
from .map import Map

ColorObjectType = Union[BaseColor, Scale, Palette, Map]


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
        if __name == '_bucket_type':
            #? Validate
            pass
        elif not isinstance(__value, self._bucket_type):
            raise TypeError(f"Colors must be of {self._bucket_type.__class__.__name__}")
        super().__setattr__(__name, __value)

    def add(self, item: ColorObjectType):
        """
        Add an item of matching type to the bucket.

        Parameters
        ----------
        item : Union[Color, Scale, Palette, Map]
            Item to add to the

        """

        if (name := item.name) is None:
            raise AttributeError(
                f"Objects need to have a name to be added to a Camp {self.__class__.__name__} Bucket"
            )
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

        return self.__dict__

    def __repr__(self):
        # TODO: re-think what I want the print of this to look like
        return str(self.__dict__)


class Camp(ColorInfo):
    """A camp of colors!"""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
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
        return self._colors

    @property
    def scales(self):
        return self._scales

    @property
    def palettes(self):
        return self._palettes

    @property
    def maps(self):
        return self._maps

    @property
    def __directory_map(self) -> Dict[str, ColorObjectType]:
        dir_map: Dict[str, ColorObjectType] = {
            "colors": BaseColor,
            "scales": Scale,
            "palettes": Palette,
            "maps": Map,
        }

        return dir_map

    @classmethod
    def load(cls, name: str, directory: Optional[Union[str,Path]] = None):
        # Search for matching directory in source locations
        if directory is None:
            # use config to find if name is in any sources
            raise NotImplementedError()
        else:
            directory = Path(directory)

        camp_dir = directory / name
        PathValidator().validate(camp_dir)

        with open(camp_dir / 'camp_info.json', "r", encoding="utf-8") as fio:
            camp_info: dict = json.load(fio)

        camp = cls(**camp_info)

        for sub_dir, klass in cls.__directory_map.items():
            search_dir: Path = camp_dir / sub_dir
            files = search_dir.glob("*.json") if search_dir.exists() else []
            for file in files:
                # TODO: what happens if there is an error loading file?
                bucket: Bucket = getattr(camp, sub_dir)
                bucket.add(klass.load_json(file))

        return camp

    def save(self, directory:Union[str, Path], overwrite=False):
        PathValidator.validate(directory)
        dest : Path = Path(directory) / self.name
        dest.mkdir(exist_ok=True)

        info_path = dest / 'camp_info.json'
        if info_path.exists() and not overwrite:
            # TODO: Check if they are same instead
            raise FileExistsError(f"file already exists for: {info_path}")

        with open(info_path, mode="w", encoding="utf-8") as fio:
            json.dump(self.info(), fio, indent=4)

        for sub_dir, _ in self.__directory_map.items():
            sub_dest_dir: Path = dest / sub_dir
            sub_dest_dir.mkdir(exist_ok=True)
            for name, color_object in getattr(self, sub_dir).__dict__.items():
                color_object: ColorSpace
                color_object.dump_json(
                    sub_dest_dir / f"{name}.json", overwrite=overwrite
                )
    
    def query_metadata(
        self,
        pattern: str,
        metadata_scope = ['keys', 'values'],
        color_object_scope : List[str] = ['colors', 'palettes', 'scales', 'maps'],
        regex: bool = True,
    )->Dict[str, Dict[str, ColorObjectType]]:
        #TODO: Arg Validation

        def matcher(text):
            if regex:
                return re.compile(pattern).match(text)
            else:
                return pattern in str(text)

        def finder(key, value):
            found = False
            # Can optimize this...
            scope_map = {'keys':key, 'values':value}
            search_in = [scope_map[scope] for scope in metadata_scope]
        
            for text in search_in:
                if matcher(text):
                    found = True

            return found

        query_results = {}
        for color_object in color_object_scope:
            bucket : Bucket = getattr(self, color_object)

            bucket_res = {key:value for key, value in bucket.to_dict().items() if finder(key, value)}

            if bucket_res:
                query_results[color_object] = bucket_res

        return query_results

