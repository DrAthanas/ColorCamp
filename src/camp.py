# Takes a path + name - creates directories
# * colors
# * Palettes
# * Scales
# * project.log


from typing import Any, Union, Optional, List
from pathlib import Path
from .color import WebColor
from .scale import Scale
from .palette import Palette


class Bucket:

    def add(self, value : Union[WebColor, Scale, Palette]):
        if (name:=value.name) is None:
            raise ValueError(f"Objects need to have a name to be added to a Camp {self.__class__.__name__} Bucket")
        if hasattr(self, name):
            raise RuntimeError(f"Name '{name}' is already in use")
        self.__setattr__(name, value)
        

    def remove(self, name: str):
        ...

    def __repr__(self):
        return str(self.__dict__)


class Camp:
    __DIR_MAP = dict(
        colors = WebColor,
        scales = Scale,
        palettes = Palette
    )

    def __init__(self, name:str, source:Union[str, Path]):
        # TODO: Add property protections to these attributes & validation
        self.name = name
        self.source = Path(source)
        self.colors = self.__Colors()
        self.scales = self.__Scales()
        self.palettes = self.__Palettes()
        self.mappings = self.__Mappings()

    @classmethod
    def load(cls, name, source:Optional[Path]=None):
        # Search for matching directory in source locations
        if source is None:
            # use config to find if name is in any sources
            raise NotImplementedError()

        camp = cls(name, source)

        for sub_dir, klass in cls.__DIR_MAP.items():
            search_dir : Path = camp.source / name / sub_dir
            files = search_dir.glob('*.json') if search_dir.exists() else []
            for file in files:
                # TODO? what happens if there is an error loading file?
                camp.__getattribute__(sub_dir).add(klass.load_json(file))

        return camp
    
    def reload(self):
        raise NotImplementedError()

    def save(self, overwrite=False):
        # writes everything to disk
        dest = self.source / self.name
        # check if name already exits
        dest.mkdir(exist_ok=True)

        for sub_dir, klass in self.__DIR_MAP.items():
            sub_dest_dir = dest / sub_dir
            sub_dest_dir.mkdir(exist_ok=True)
            for name, _ in self.__getattribute__(sub_dir).__dict__.items():
                (
                    self
                    .__getattribute__(sub_dir)
                    .__getattribute__(name)
                    .dump_json(sub_dest_dir / f'{name}.json', overwrite = overwrite)
                )

    def query(self):
        # search for colors & palettes
        raise NotImplementedError()

    class __Colors(Bucket):
        def __setattr__(self, __name: str, __value: WebColor) -> None:
            if not isinstance(__value, WebColor):
                raise TypeError("Colors must be of WebColor")
            super().__setattr__(__name, __value)
    

    class __Scales(Bucket):
        def __setattr__(self, __name: str, __value: Scale) -> None:
            if not isinstance(__value, Scale):
                raise TypeError("Scales must be a Scale")


    class __Palettes(Bucket):
        def __setattr__(self, __name: str, __value: Palette) -> None:
            if not isinstance(__value, Palette):
                raise TypeError("Palettes must be a Palette")


    class __Mappings(Bucket):
        pass

    
    
    