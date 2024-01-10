import pytest

from bs4 import BeautifulSoup

from colorcamp import Color, Scale

# TODO:
# * test print
# * test get_color
# * test exceptions

@pytest.fixture(scope="class")
def cls_scale(request):
    sky_hex: Color = request.getfixturevalue('sky_Color').to_hex()
    pink_hex: Color = request.getfixturevalue("pink_hex")
    mustard_hex: Color = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: Color = request.getfixturevalue("lime_hsl").to_hex()

    request.cls.scale: Scale = Scale(
        colors = [sky_hex, pink_hex, mustard_hex, lime_hex],
        name = 'example',
        description = 'A beautiful color palette',
        metadata = {'categoral':'four colors'},
    )


@pytest.mark.usefixtures('cls_scale')
class TestScale:
    """test scale"""

    def test_tupliness(self):
        assert isinstance(self.scale, tuple)
        assert self.scale[1] == "#FF15AA"
        assert "#FF15AA" in self.scale
        with pytest.raises(TypeError) as e_info:
            self.scale[2] = 123

    def test_repr_html(self):
        assert bool(BeautifulSoup(self.scale._repr_html_(), "html.parser").find())


