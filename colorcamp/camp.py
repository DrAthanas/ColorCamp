from typing import Any, Union, Optional, Dict
from pathlib import Path
from .color import WebColor
from .scale import Scale
from .palette import Palette

ColorObjectType = Union[type[WebColor], type[Palette], type[Scale]]
ColorObject = Union[WebColor, Scale, Palette]


class Bucket:
    def __init__(self, bucket_type: ColorObjectType):
        self._bucket_type = bucket_type

    def __setattr__(self, __name: str, __value: Any) -> None:
        if not isinstance(__value, self._bucket_type):
            raise TypeError(f"Colors must be of {self._bucket_type.__class__.__name__}")
        super().__setattr__(__name, __value)

    def add(self, item: ColorObject):
        """
        Add an item of mtching type to the bucket.

        Parameters
        ----------
        item : Union[WebColor, Scale, Palette]
            Item to add to the

        """
        if (name := item.name) is None:
            raise ValueError(
                f"Objects need to have a name to be added to a Camp {self.__class__.__name__} Bucket"
            )
        if hasattr(self, name):
            raise RuntimeError(f"Name '{name}' is already in use")
        setattr(self, name, item)

    def remove(self, name: str):
        if not hasattr(self, name):
            raise RuntimeError(f"Name '{name} is not in bucket")
        delattr(self, name)

    def __repr__(self):
        # TODO: re-think what I want the print of this to look like
        return str(self.__dict__)


class Camp:
    __DIR_MAP: Dict[str, ColorObjectType] = {
        "colors": WebColor,
        "scales": Scale,
        "palettes": Palette,
    }

    def __init__(self, name: str, source: Union[str, Path]):
        # TODO: Add property protections to these attributes & validation
        self.name = name
        self.source = Path(source)
        self.colors = Bucket(bucket_type=WebColor)
        self.scales = Bucket(bucket_type=Scale)
        self.palettes = Bucket(bucket_type=Palette)
        # self.mappings = self._Mappings()

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

    @classmethod
    def load(cls, name: str, source: Optional[Path] = None):
        # Search for matching directory in source locations
        if source is None:
            # use config to find if name is in any sources
            raise NotImplementedError()

        camp = cls(name, source)

        for sub_dir, klass in cls.__DIR_MAP.items():
            search_dir: Path = camp.source / name / sub_dir
            files = search_dir.glob("*.json") if search_dir.exists() else []
            for file in files:
                # TODO? what happens if there is an error loading file?
                bucket: Bucket = getattr(camp, sub_dir)
                bucket.add(klass.load_json(file))

        return camp

    def reload(self):
        raise NotImplementedError()

    def save(self, overwrite=False):
        # writes everything to disk
        dest = self.source / self.name
        # check if name already exits
        dest.mkdir(exist_ok=True)

        for sub_dir, _ in self.__DIR_MAP.items():
            sub_dest_dir: Path = dest / sub_dir
            sub_dest_dir.mkdir(exist_ok=True)
            for name, color_object in getattr(self, sub_dir).__dict__.items():
                color_object: ColorObject
                color_object.dump_json(
                    sub_dest_dir / f"{name}.json", overwrite=overwrite
                )

    def query(self):
        # search for colors & palettes
        raise NotImplementedError()

    # class _Colors(Bucket):
    #     def __setattr__(self, __name: str, __value: WebColor) -> None:
    #         if not isinstance(__value, WebColor):
    #             raise TypeError("Colors must be of WebColor")
    #         super().__setattr__(__name, __value)

    # class _Scales(Bucket):
    #     def __setattr__(self, __name: str, __value: Scale) -> None:
    #         if not isinstance(__value, Scale):
    #             raise TypeError("Scales must be a Scale")

    # class _Palettes(Bucket):
    #     def __setattr__(self, __name: str, __value: Palette) -> None:
    #         if not isinstance(__value, Palette):
    #             raise TypeError("Palettes must be a Palette")

    # class _Mappings(Bucket):
    #     pass
