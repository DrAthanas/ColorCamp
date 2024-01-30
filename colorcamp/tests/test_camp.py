from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from colorcamp._camp import Camp
from colorcamp.color_objects.color_space import BaseColor
from colorcamp.color_objects import Map, Scale, Palette

pytest.fixture(scope="class")


def cls_map(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: BaseColor = request.getfixturevalue("pink_hex")
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    camp = Camp(
        name="TestCamp",
        description="A group of colors and color objects",
        metadata={"version": "0.1.0"},
    )

    camp.colors.add(sky_hex)
    camp.colors.add(pink_hex)
    camp.colors.add(mustard_hex)
    camp.colors.add(lime_hex)

    camp.palettes.add(Palette((sky_hex, pink_hex, mustard_hex, lime_hex), name="Pal"))
    camp.palettes.add(Scale(camp.palettes.Pal, name="lette"))
    camp.palettes.add(Map({"mustard": mustard_hex, "lime": lime_hex}, name="GoodFood"))

    request.cls.camp: Camp = camp
