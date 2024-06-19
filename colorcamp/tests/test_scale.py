from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from bs4 import BeautifulSoup

from colorcamp.color_space import BaseColor
from colorcamp.groups import Scale


@pytest.fixture(scope="class")
def cls_scale(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: BaseColor = request.getfixturevalue("pink_hex")
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    request.cls.scale: Scale = Scale(
        colors=[sky_hex, pink_hex, mustard_hex, lime_hex],
        name="example",
        description="A beautiful color scale",
        metadata={"continuous ": "four color stops"},
    )


@pytest.mark.usefixtures("cls_scale")
class TestScale:
    """test scale"""

    def test_tupliness(self):
        assert isinstance(self.scale, tuple)
        assert self.scale[1].equivalence("#FF15AA")
        assert "#FF15AA" in self.scale
        with pytest.raises(TypeError) as e_info:
            self.scale[2] = 123

    def test_repr_html(self):
        assert bool(BeautifulSoup(self.scale._repr_html_(), "html.parser").find())

    def test_save_and_load(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            scale_path = temp_dir / f"{self.scale.name}"
            self.scale.dump_json(scale_path)
            reloaded_scale = Scale.load_json(scale_path)

        assert self.scale == reloaded_scale

    def test_reverse(self):
        reversed_scale = self.scale.reverse()

        assert self.scale.info() == reversed_scale.info()
        assert self.scale.colors[::-1] == reversed_scale.colors


def test_not_color_objects(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: str = "#FF15AA"
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    with pytest.raises(TypeError):
        test_scale = Scale(
            colors=[sky_hex, pink_hex, mustard_hex, lime_hex],
            name="example",
            description="A beautiful color scale",
            metadata={"continuous ": "four color stops"},
        )


@pytest.mark.parametrize(
    "stops",
    [
        (0, 0.5, 1),  # wrong number of stops
        (0, 0.25, 1, 0.5),  # not in order
    ],
)
def test_invalid_stops(request, stops):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: BaseColor = request.getfixturevalue("pink_hex")
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    with pytest.raises(ValueError):
        Scale(
            colors=[sky_hex, pink_hex, mustard_hex, lime_hex],
            stops=stops,
            name="example",
            description="A beautiful color scale",
            metadata={"continuous ": "four color stops"},
        )
