import pytest

from bs4 import BeautifulSoup

from colorcamp import Color, Palette

@pytest.fixture(scope="class")
def cls_palette(request):
    sky_hex: Color = request.getfixturevalue('sky_Color').to_hex()
    pink_hex: Color = request.getfixturevalue("pink_hex")
    mustard_hex: Color = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: Color = request.getfixturevalue("lime_hsl").to_hex()

    request.cls.palette: Palette = Palette(
        colors = [sky_hex, pink_hex, mustard_hex, lime_hex],
        name = 'example',
        description = 'A beautiful color palette',
        metadata = {'categoral':'four colors'},
    ) 


@pytest.mark.usefixtures('cls_palette')
class TestPalette:
    """test palette"""

    def test_tupliness(self):
        assert isinstance(self.palette, tuple)
        assert self.palette[1] == "#FF15AA"
        assert "#FF15AA" in self.palette
        with pytest.raises(TypeError) as e_info:
            self.palette[2] = 123

    def test_repr_html(self):
        assert bool(BeautifulSoup(self.palette._repr_html_(), "html.parser").find())

    def test_inf_cycle(self):
        for i in range(len(self.palette)*2):
            assert self.palette[i % len(self.palette)] == self.palette.next()

    def test_print(self):
        assert repr(self.palette) == "Palette('#0FB6FF', '#FF15AA', '#FFAA15', '#14FFAA')"
