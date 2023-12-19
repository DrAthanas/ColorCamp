"""Tests for color module"""
import pytest
from functools import partial
from tempfile import TemporaryDirectory
from pathlib import Path

from bs4 import BeautifulSoup

from colorcamp import WebColor, Hex, RGB, HSL
from colorcamp.common.validators import HexStringValidator

# TODO:
# * alpha
# * Subclasses
#   * css
#   * registration
# * add

param_colors = partial(
    pytest.mark.parametrize(
        'color',
        [
            ('sky_webcolor'),
            ('pink_hex'),
            ('mustard_rgb'),
            ('lime_hsl'),
        ]
    )
)

param_color_types = partial(
    pytest.mark.parametrize(
        'color_type',
        [
            'WebColor',
            'Hex',
            'RGB',
            'HSL',
        ]
    )
)


@param_colors
def test_attr_name(color, request):
    color_obj: WebColor = request.getfixturevalue(color)
    assert color_obj.name == color

@pytest.mark.usefixtures('cls_sky_webcolor')
class TestWebColor:
    """Test webcolor"""
    def test_name(self, ):
        assert isinstance(self.color.name, str)
    
    def test_metadata(self):
        #TODO: Fill in actual test
        pass

    def test_description(self):
        assert isinstance(self.color.description, str)

    def test_rgb_linear(self):
        assert isinstance(self.color.rgb_linear, tuple)
        assert all([0 <= value <= 1 for value in self.color.rgb_linear])
        assert 2 < len(self.color.rgb_linear) < 5

    def test_alpha(self):
        assert self.color.alpha is None

    def test_change_alpha(self):
        new_color = self.color.change_alpha(0.7)
        assert new_color != self.color
        assert new_color.alpha == 0.7

    def test_rgb(self):
        assert all([isinstance(channel, int) for channel in self.color.rgb])
        assert all([0<=channel<=255 for channel in self.color.rgb])
        # TODO: update with real validator

    def test_hex(self):
        assert HexStringValidator().validate(self.color.hex) is None

    def test_hsl(self):
        # TODO: update with real validator
        pass

    def test_info(self):
        info = self.color.info()
        assert set(info.keys()) == {'name', 'description', 'metadata'}

    def test_repr_html(self):
        # Use beautiful soup to validate HTML
        assert bool(BeautifulSoup(self.color._repr_html_(), "html.parser").find())


@pytest.mark.usefixtures('cls_pink_hex')
class TestHex(TestWebColor):
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
        hex_color:Hex = self.color
        assert not isinstance(str(hex_color), Hex)
        assert hex_color.isupper()

    def test_stringiness(self):
        hex_color : Hex = self.color
        # Is it a string?
        assert isinstance(hex_color, str)
        # Do string methods still work?
        assert hex_color.lower() == '#ff15aa'
        assert hex_color[-2:] == 'AA'


@pytest.mark.usefixtures('cls_mustard_rgb')
class TestRGB(TestWebColor):
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


@pytest.mark.usefixtures('cls_lime_hsl')
class TestHSL(TestWebColor):
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


@param_colors
@param_color_types
def test_conversion(color_type, color, request):
    color_obj: WebColor = request.getfixturevalue(color)
    new_color = color_obj.to_color_type(color_type)
    assert new_color.__class__.__name__ == color_type

#TODO: test loss of precision
@param_colors
@param_color_types
def test_conversion_equality(color_type, color, request):
    color_obj: WebColor = request.getfixturevalue(color)
    new_color = color_obj.to_color_type(color_type)
    assert new_color == color_obj

# use some standard Web conversion tools to validate
def test_addition():
    pass

# fmt: off
@pytest.mark.parametrize(
    ['color', 'other_color'],
    [
        ('sky_webcolor', RGB((15,182,255), name = 'anything')),
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
    color_obj: WebColor = request.getfixturevalue(color) 
    assert color_obj == other_color    

@param_colors
def test_save_and_load(color, request):
    color_obj: WebColor = request.getfixturevalue(color)
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        color_path = temp_dir / f"{color_obj.name}"
        color_obj.dump_json(color_path)
        reloaded_color = WebColor.load_json(color_path, color_obj.__class__.__name__)

