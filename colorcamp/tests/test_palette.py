from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from bs4 import BeautifulSoup

from colorcamp.color_space import BaseColor
from colorcamp.groups import Palette


@pytest.fixture(scope="class")
def cls_palette(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: BaseColor = request.getfixturevalue("pink_hex")
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    request.cls.palette: Palette = Palette(
        colors=[sky_hex, pink_hex, mustard_hex, lime_hex],
        name="example",
        description="A beautiful color palette",
        metadata={"categorical": "four colors"},
    )


@pytest.mark.usefixtures("cls_palette")
class TestPalette:
    """test palette"""

    def test_tupliness(self):
        assert isinstance(self.palette, tuple)
        assert self.palette[1].equivalence("#FF15AA")
        assert "#FF15AA" in self.palette
        with pytest.raises(TypeError) as e_info:
            self.palette[2] = 123

    def test_repr_html(self):
        assert bool(BeautifulSoup(self.palette._repr_html_(), "html.parser").find())

    def test_inf_cycle(self):
        for i in range(len(self.palette) * 2):
            assert self.palette[i % len(self.palette)] == self.palette.next()

    def test_print(self):
        assert repr(self.palette) == "Palette('#0FB6FF', '#FF15AA', '#FFAA15', '#15FFAA')"

    def test_save_and_load(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            color_path = temp_dir / f"{self.palette.name}"
            self.palette.dump_json(color_path)
            reloaded_palette = Palette.load_json(color_path)

        assert self.palette == reloaded_palette

    def test_maintain_equality(self):
        colors = self.palette.colors
        assert self.palette == colors
        # Check that it is no longer a Palette
        assert isinstance(colors, tuple) and not isinstance(colors, Palette)

    def test_reverse(self):
        reversed_pal = self.palette.reverse()

        assert self.palette.info() == reversed_pal.info()
        assert self.palette.colors[::-1] == reversed_pal.colors


def test_not_color_objects(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: str = "#FF15AA"
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    with pytest.raises(TypeError):
        test_pal = Palette(
            colors=[sky_hex, pink_hex, mustard_hex, lime_hex],
            name="example",
            description="A beautiful color palette",
            metadata={"categorical": "four colors"},
        )
