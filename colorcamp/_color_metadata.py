"""Common properties for all color derivatives"""

import json
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union

from colorcamp.common.types import ColorSpace
from colorcamp.common.validators import (
    DescriptionValidator,
    NameValidator,
    PathValidator,
)

__all__ = [
    "ColorInfo",
    "ColorSerializer",
    "MetaColor",
]


class ColorInfo:
    """Basic metadata to be attributed to all color objects"""

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Color info to be inherited by other Color objects and containers

        Parameters
        ----------
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """
        self.name = name
        self.description = description
        self.metadata = metadata  # type: ignore

    @property
    def name(self) -> Union[str, None]:
        """Object descriptive name : str"""
        return self._name

    @name.setter
    def name(self, value: Union[str, None]):
        if hasattr(self, "_name"):
            raise AttributeError("can't set attribute 'name'")

        if value is not None:
            NameValidator().validate(value)
        self._name = value

    @property
    def description(self) -> Union[str, None]:
        """Short descriptive text : str"""
        return self._description

    @description.setter
    def description(self, value: Union[str, None]):
        if hasattr(self, "_description"):
            raise AttributeError("can't set attribute 'description'")

        if value is not None:
            DescriptionValidator().validate(value)
        self._description = value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Unstructured metadata : Dict[hashable, Any]"""
        return self._metadata

    @metadata.setter
    def metadata(self, value: Union[Dict[str, Any], None]):
        if hasattr(self, "_metadata"):
            raise AttributeError("can't set attribute 'metadata'")

        if value is None:
            value = {}
        self._metadata = value

    def info(self) -> Dict[str, Any]:
        """Get all object descriptive info

        Returns
        -------
        Dict[str, Any]
            A dictionary with keys: name, description, metadata
        """

        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


class ColorSerializer:
    """Serialization of Colors and Color Objects"""

    @classmethod
    @abstractmethod
    def from_dict(cls, *args, **kwargs):
        """abstract method, from dict"""
        return

    @classmethod
    def load_json(cls, file_path: Union[str, Path], color_space: Optional[ColorSpace] = None):
        """Load object from JSON file on disk

        Parameters
        ----------
        file_path : Union[str, Path]
            Source file path to load data from
        color_space : Optional[ColorSpace], optional
            _description_, by default None

        Returns
        -------
        Any, CurrentClass
            an object matching the type of the class that this method was called from

        """
        PathValidator().validate(file_path)

        with open(file_path, "r", encoding="utf-8") as fio:
            color_dict: dict = json.load(fio)

        return cls.from_dict(color_dict, color_space)

    @abstractmethod
    def to_dict(self):
        """abstract method, to dict"""
        return

    def dump_json(self, file_path: Union[str, Path], overwrite: bool = False) -> None:
        """Save the object as a JSON file

        Parameters
        ----------
        file_path : Union[str, Path]
            Sink file path to save the object
        overwrite : bool, optional
            Overwrite an existing file if necessary, by default False

        Raises
        ------
        FileExistsError
            If overwrite is `False` and the file exists

        """
        PathValidator().validate(file_path)
        file_path = Path(file_path)
        if file_path.exists() and not overwrite:
            raise FileExistsError(f"file already exists for: {file_path}")

        with open(file_path, mode="w", encoding="utf-8") as fio:
            json.dump(self.to_dict(), fio, indent=4)


# Unused argument, abstract method not overwritten
# pylint: disable=W0613, disable=W0223
class MetaColor(ColorInfo, ColorSerializer):
    """All Colors and Color container objects will have some common metadata and functionality"""

    def __init__(
        self,
        *args,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Color metadata to be inherited by other Color objects and containers

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

    def change_info(
        self,
        **kwargs,
    ):
        """Change metadata for a Color Object, this will return a new object

        Accepted Parameters
        ----------
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """

        accepted_values = ["name", "description", "metadata"]

        new_info = {val: kwargs.pop(val) for val in accepted_values if val in kwargs}

        if not new_info:
            raise ValueError("No metadata arguments to change")
        if kwargs:
            raise ValueError(f".change_info got an unexpected keyword argument(s) {', '.join(kwargs.keys())}")

        return self.from_dict(
            {
                **self.to_dict(),
                **new_info,
            }
        )


# pylint: enable=W0613, enable=W0223
