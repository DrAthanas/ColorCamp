from typing import Protocol, Union
from .types import Numeric
import re
from .exceptions import (
    NumericIntervalError
)
# TODO:
# * Metadata Validator
# * Consider Validators for RGB, HSL
# * ? class validators?
# ? Move None checks in here?

class IValidator(Protocol):
    """ Generic validator """

    def validate(self, *args, **kwargs) -> None:
        """ Validate the person """
        raise NotImplementedError("validate not implemented")


class UnitIntervalValidator(IValidator):
    """ Unit interval validator"""

    def __init__(self, min:Numeric, max:Numeric, name:str='value'):
        self.min = min
        self.max = max
        self.name = name

    def validate(self, value:Union[int, float])->None:
        if not isinstance(value, Numeric):
            raise TypeError(f"{self.name} should be a Numeric[int, float]")
        if not (self.min <= value <= self.max):
            raise NumericIntervalError(f"{self.name} ({value}) is out side of interval range [{self.min}, {self.max}]")

        
class FractionIntervalValidator(UnitIntervalValidator):
    """Fraction interval validator [0,1]"""
    def __init__(self, name='value'):
        super().__init__(min=0, max=1, name=name)


class HueIntervalValidator(UnitIntervalValidator):
    """Hue interval validator [0,360]"""
    def __init__(self):
        self.name = 'hue'
        super().__init__(min=0, max=360)


class RGB256IntervalValidator(UnitIntervalValidator):
    """RGB interval validator [0,255]"""
    def __init__(self, name:str='256 RGB'):
        super().__init__(min=0, max=255, name = name)


class RegexValidator(IValidator):
    """Regex validator template"""

    def __init__(self, regex_pattern:str, name:str = 'string'):
        self.regex = re.compile(regex_pattern)
        self.name = name

    def validate(self, string: str) -> None:
        if not isinstance(string, str):
            raise TypeError(f'{self.name} should be a string')
        elif not self.regex.match(string):
            #? more descriptive error
            raise ValueError(f'invalid {self.name}: {string}')


class NameValidator(RegexValidator):
    """Name string validator"""

    def __init__(self):
        self.regex = re.compile(
            r'^[a-zA-Z0-9_]+$'
        )
        self.name = 'name'

    def validate(self, string: Union[str, None]) -> None:
        if string is None:
            return
        return super().validate(string) 


class HexStringValidator(RegexValidator):
    """Hex string validator"""

    def __init__(self):
        self.regex = re.compile(
            r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
        )
        self.name = 'hex code'

        
class DescriptionValidator(IValidator):
    """Description string validator"""

    def __init__(self):
        pass

    def validate(self, description_string:Union[str, None]) -> None:
        if description_string is None:
            return
        if not isinstance(description_string, str):
            raise TypeError('description should be a string')
        if len(description_string) > 255:
            #? Make this a warning?
            raise ValueError('description should not be more than 255 characters')