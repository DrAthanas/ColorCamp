from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Mapping

import pytest
from bs4 import BeautifulSoup

from colorcamp.color_space import BaseColor
from colorcamp.groups import Map


@pytest.fixture(scope="class")
def cls_map(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: BaseColor = request.getfixturevalue("pink_hex")
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    request.cls.map: Map = Map(
        color_map={
            "sky": sky_hex,
            "pink": pink_hex,
            "mustard": mustard_hex,
            "lime": lime_hex,
        },
        name="example",
        description="A beautiful color map",
        metadata={"mapping": "four colors"},
    )


@pytest.mark.usefixtures("cls_map")
class TestMap:
    """test map"""

    def test_mapping(self):
        assert isinstance(self.map, Mapping)
        assert self.map["pink"].equivalence("#FF15AA")
        assert "pink" in self.map
        assert "#FF15AA" in self.map.values()
        with pytest.raises(TypeError) as e_info:
            self.map[2] = 123

    def test_repr_html(self):
        assert bool(BeautifulSoup(self.map._repr_html_(), "html.parser").find())

    def test_save_and_load(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            color_path = temp_dir / f"{self.map.name}"
            self.map.dump_json(color_path)
            reloaded_map = Map.load_json(color_path)

        assert self.map == reloaded_map

    def test_colors_attr(self):
        assert self.map.colors == tuple(self.map.values())


def test_not_color_objects(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: str = "#FF15AA"
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    with pytest.raises(TypeError):
        test_map = Map(
            color_map={
                "sky": sky_hex,
                "pink": pink_hex,
                "mustard": mustard_hex,
                "lime": lime_hex,
            },
            name="example",
            description="A beautiful color map",
            metadata={"mapping": "four colors"},
        )
