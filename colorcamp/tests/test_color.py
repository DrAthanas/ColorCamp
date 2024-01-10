"""Tests for color module"""
from tempfile import TemporaryDirectory
from pathlib import Path

from bs4 import BeautifulSoup
import pytest

from colorcamp.color import Color, Hex, RGB, HSL
from colorcamp.common.validators import HexStringValidator
from colorcamp.common.exceptions import NumericIntervalError
from conftest import (
    param_color_init,
    param_colors,
    param_color_types,
    param_hex_codes,
    param_rgb_values,
    param_hsl_values,
)

# TODO:
# * alpha
# * Subclasses
#   * registration
# * add

@param_colors
def test_attr_name(color, request):
    color_obj: Color = request.getfixturevalue(color)
    assert color_obj.name == color

@param_color_init
def test_fractional_interval_validator(params):
    with pytest.raises(NumericIntervalError):
        Color(**params)

@pytest.mark.usefixtures("cls_sky_Color")
class TestColor:
    """Test Color"""

    def test_name(
        self,
    ):
        assert isinstance(self.color.name, str)

    def test_metadata(self):
        # TODO: Fill in actual test
        pass

    def test_description(self):
        assert isinstance(self.color.description, str)

    def test_fractional_rgb(self):
        assert isinstance(self.color.fractional_rgb, tuple)
        assert all([0 <= value <= 1 for value in self.color.fractional_rgb])
        assert 2 < len(self.color.fractional_rgb) < 5

    def test_alpha(self):
        assert self.color.alpha is None

    def test_change_alpha(self):
        new_color : Color = self.color.change_alpha(0.7)
        assert new_color != self.color
        assert new_color.alpha == 0.7
        ## a bit funky of an assert
        assert new_color.rgb[3] == 0.7
        assert new_color.fractional_rgb[3] == 0.7
        assert new_color.hsl[3] == 0.7
        assert new_color.hex[-2:] == 'B2'

    def test_rgb(self):
        assert all([isinstance(channel, int) for channel in self.color.rgb])
        assert all([0 <= channel <= 255 for channel in self.color.rgb])
        # TODO: update with real validator

    def test_hex(self):
        assert HexStringValidator().validate(self.color.hex) is None

    def test_hsl(self):
        # TODO: update with real validator
        pass

    def test_info(self):
        info = self.color.info()
        assert set(info.keys()) == {"name", "description", "metadata"}

    def test_repr_html(self):
        # Use beautiful soup to validate HTML
        assert bool(BeautifulSoup(self.color._repr_html_(), "html.parser").find())
            
    def test_alpha_setter(self):
        with pytest.raises(AttributeError):
            self.color.alpha = 0.9
    
    def test_rgb_setter(self):
        with pytest.raises(AttributeError):
            self.color.fractional_rgb = (0.1, 0.4, 0.5)


@pytest.mark.usefixtures("cls_pink_hex")
class TestHex(TestColor):
    """Test hex color"""

    def test_channels(self):
        assert self.color.red == 255
        assert self.color.green == 21
        assert self.color.blue == 170

    def test_change_channel(self):
        assert self.color.change_red(144).red == 144
        assert self.color.change_green(144).green == 144
        assert self.color.change_blue(144).blue == 144

    def test_str(self):
        hex_color: Hex = self.color
        assert not isinstance(str(hex_color), Hex)
        assert hex_color.isupper()

    def test_stringiness(self):
        hex_color: Hex = self.color
        # Is it a string?
        assert isinstance(hex_color, str)
        # Do string methods still work?
        assert hex_color.lower() == "#ff15aa"
        assert hex_color[-2:] == "AA"

    @param_hex_codes
    def test_create_hex(self, hex_code):
        assert isinstance(Hex(hex_code), Hex)

    def test_hex_setter(self):
        with pytest.raises(AttributeError):
            self.color.hex = '#FFFFFF'


@pytest.mark.usefixtures("cls_mustard_rgb")
class TestRGB(TestColor):
    """Test rgb color"""

    def test_channels(self):
        assert self.color.red == 255
        assert self.color.green == 170
        assert self.color.blue == 21

    def test_change_channel(self):
        assert self.color.change_red(144).red == 144
        assert self.color.change_green(144).green == 144
        assert self.color.change_blue(144).blue == 144

    def test_rgb_tupleness(self):
        assert isinstance(self.color, tuple)
        assert self.color[0] == self.color.red
        assert 170 in self.color
        with pytest.raises(TypeError) as e_info:
            self.color[2] = 123

    @param_rgb_values
    def test_create_rgb(self, rgb):
        assert RGB(rgb).rgb == rgb

    def test_rgb_setter(self):
        with pytest.raises(AttributeError):
            self.color.rgb = (200, 123, 23)



@pytest.mark.usefixtures("cls_lime_hsl")
class TestHSL(TestColor):
    def test_channels(self):
        assert self.color.hue == 158.2051282051282
        assert self.color.saturation == 0.9999999999999999
        assert self.color.lightness == 0.5411764705882353

    def test_change_channel(self):
        assert self.color.change_hue(144).hue == 144
        assert self.color.change_saturation(0.5).saturation == 0.5
        assert self.color.change_lightness(0.5).lightness == 0.5

    def test_hsl_tupleness(self):
        assert isinstance(self.color, tuple)
        assert self.color[0] == self.color.hue
        with pytest.raises(TypeError) as e_info:
            self.color[2] = 123

    @param_hsl_values
    def test_create_rgb(self, hsl):
        assert HSL(hsl) == hsl

    def test_hsl_setter(self):
        with pytest.raises(AttributeError):
            self.color.hsl = (200, 0.7, 0.5)


@param_colors
@param_color_types
def test_conversion(color_type, color, request):
    color_obj: Color = request.getfixturevalue(color)
    new_color = color_obj.to_color_type(color_type)
    assert new_color.__class__.__name__ == color_type

@param_colors
@param_color_types
def test_conversion_equality(color_type, color, request):
    color_obj: Color = request.getfixturevalue(color)
    new_color = color_obj.to_color_type(color_type)
    assert new_color == color_obj


# use some standard Web conversion tools to validate
def test_addition():
    pass


# fmt: off
@pytest.mark.parametrize(
    ['color', 'other_color'],
    [
        ('sky_Color', RGB((15,182,255), name = 'anything')),
        ('pink_hex', RGB((255,21,170))),
        ('pink_hex', Hex("#FF15AA")),
        ('pink_hex', "#FF15AA"),
        pytest.param('pink_hex', (255,21,170), marks = [pytest.mark.xfail]),
        ('mustard_rgb', RGB((255,170,21))),
        ('mustard_rgb', Hex("#FFAA15")),
        ('mustard_rgb', (255,170,21)),
        ('lime_hsl', HSL((158.2051282051282, 0.9999999999999999, 0.5411764705882353))),
        ('lime_hsl', Hex("#15FFAA")),
        ('lime_hsl', (158.2051282051282, 0.9999999999999999, 0.5411764705882353))
    ]
) # fmt: on
def test_equality(color, other_color, request):
    color_obj: Color = request.getfixturevalue(color) 
    assert color_obj == other_color    

@param_colors
def test_save_and_load(color, request):
    color_obj: Color = request.getfixturevalue(color)
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        color_path = temp_dir / f"{color_obj.name}"
        color_obj.dump_json(color_path)
        reloaded_color = color_obj.load_json(color_path)

    assert color_obj == reloaded_color    