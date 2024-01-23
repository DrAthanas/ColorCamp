from pathlib import Path

import pytest
from pytest import param, mark

from colorcamp.common.exceptions import NumericIntervalError
from conftest import param_hex_codes, param_color_types

from colorcamp.common.validators import (
    FractionIntervalValidator,
    HueIntervalValidator,
    RGB256IntervalValidator,
    NameValidator,
    HexStringValidator,
    DescriptionValidator,
    PathValidator,
    ColorTypeValidator,
)


@pytest.mark.parametrize(
    "value",
    [
        0,
        1,
        0.5,
        param(-1, marks=mark.xfail(NumericIntervalError, reason="less that 0")),
        param(2, marks=mark.xfail(NumericIntervalError, reason="above that 1")),
        param("1", marks=mark.xfail(TypeError, reason="not a numeric")),
    ],
)
def test_fraction_interval_validator(value):
    FractionIntervalValidator().validate(value)


@pytest.mark.parametrize(
    "value",
    [
        0,
        360,
        344.5,
        param(-1, marks=mark.xfail(NumericIntervalError, reason="less that 0")),
        param(361, marks=mark.xfail(NumericIntervalError, reason="above that 360")),
        param("1", marks=mark.xfail(TypeError, reason="not a numeric")),
    ],
)
def test_hue_interval_validator(value):
    HueIntervalValidator().validate(value)


@pytest.mark.parametrize(
    "value",
    [
        0,
        255,
        123.5,
        param(-1, marks=mark.xfail(NumericIntervalError, reason="less that 0")),
        param(256, marks=mark.xfail(NumericIntervalError, reason="above that 255")),
        param("12", marks=mark.xfail(TypeError, reason="not a numeric")),
    ],
)
def test_hue_interval_validator(value):
    RGB256IntervalValidator().validate(value)


@pytest.mark.parametrize(
    "value",
    [
        "argus",
        "Cyan_000",
        "345",
        None,
        param(345, marks=mark.xfail(TypeError, reason="empty strings are not valid")),
        param("", marks=mark.xfail(ValueError, reason="empty strings are not valid")),
        param(".hidden", marks=mark.xfail(ValueError, reason="contains '.' ")),
        param("inva/id", marks=mark.xfail(ValueError, reason="contains '/'")),
    ],
)
def test_name_validator(value):
    NameValidator().validate(value)


@param_hex_codes
def test_hex_validator(hex_code):
    HexStringValidator().validate(hex_code)


@pytest.mark.parametrize(
    "value",
    [
        "Ispom lorem",
        None,
        param("A" * 1000, marks=mark.xfail(ValueError, reason="too long")),
        param(1234, marks=mark.xfail(ValueError, reason="not a string")),
    ],
)
def test_description_validator(value):
    DescriptionValidator().validate(value)


@pytest.mark.parametrize(
    "value",
    [
        "/test/something",
        Path.cwd(),
        param(1234, marks=mark.xfail(TypeError, reason="Not a string or path")),
    ],
)
def test_path_validator(value):
    PathValidator().validate(value)


@pytest.mark.parametrize(
    "color_type",
    [
        "Color",
        "Hex",
        "RGB",
        "HSL",
        param("Argus", marks=mark.xfail(TypeError, reason="Not a color literal")),
        param(1234, marks=mark.xfail(TypeError, reason="Not a color literal")),
    ],
)
def test_color_type_validator(color_type):
    ColorTypeValidator().validate(color_type)
