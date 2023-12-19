"""Common properties for all color derivatives"""
from typing import Optional, Dict, Any, Union
from .common.validators import (
    NameValidator,
    DescriptionValidator
)

class ColorMetadata:

    def __init__(
        self, name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.metadata = metadata

    @property
    def name(self) -> Union[str, None]:
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
        return self._metadata

    @metadata.setter
    def metadata(self, value: Union[Dict[str, Any], None]):
        if hasattr(self, "_metadata"):
            raise AttributeError("can't set attribute 'metadata'")

        if value is None:
            value = {}
        self._metadata = value
