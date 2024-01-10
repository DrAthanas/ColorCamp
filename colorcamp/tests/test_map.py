import pytest
from typing import Mapping

from bs4 import BeautifulSoup

from colorcamp import Color, Map

@pytest.fixture(scope="class")
def cls_map(request):
    sky_hex: Color = request.getfixturevalue('sky_Color').to_hex()
    pink_hex: Color = request.getfixturevalue("pink_hex")
    mustard_hex: Color = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: Color = request.getfixturevalue("lime_hsl").to_hex()

    request.cls.map: Map = Map(
        color_map = {
            'sky' : sky_hex, 
            'pink' : pink_hex, 
            'mustard' : mustard_hex, 
            'lime' : lime_hex,
        },
        name = 'example',
        description = 'A beautiful color palette',
        metadata = {'categoral':'four colors'},
    )

@pytest.mark.usefixtures('cls_map')
class TestMap:
    """test map"""

    def test_mapping(self):
        assert isinstance(self.map, Mapping)
        assert self.map['pink'] == "#FF15AA"
        assert "pink" in self.map
        assert "#FF15AA" in self.map.values()
        with pytest.raises(TypeError) as e_info:
            self.map[2] = 123

    def test_repr_html(self):
        assert bool(BeautifulSoup(self.map._repr_html_(), "html.parser").find())
