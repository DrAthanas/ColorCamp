from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from copy import copy

from colorcamp._camp import Camp
from colorcamp.color_objects.color_space import BaseColor
from colorcamp.color_objects import Map, Scale, Palette
from colorcamp.color_objects import Hex
from colorcamp._settings import settings

@pytest.fixture(scope="class")
def cls_camp(request):
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
    camp.scales.add(Scale(camp.palettes.Pal, name="lette"))
    camp.maps.add(Map({"mustard": mustard_hex, "lime": lime_hex}, name="GoodFood"))

    request.cls.camp: Camp = camp


@pytest.mark.usefixtures('cls_camp')
class TestCamp:
    """testing Camp"""

    def test_save_and_load(self):
        camp : Camp = self.camp

        with TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)

            camp.save(tempdir)

            new_camp = camp.load('TestCamp', tempdir)

            assert new_camp.colors.pink_hex == camp.colors.pink_hex
            assert new_camp.palettes.Pal == camp.palettes.Pal
            assert new_camp.scales.lette == camp.scales.lette

    def test_no_name(self):
        with pytest.raises(AttributeError):
            self.camp.colors.add(Hex('#66FF66'))

    def test_name_in_use(self):
        with pytest.raises(ValueError):
            self.camp.colors.add(Hex('#66FF66', name = 'pink_hex'))

    def test_remove_co(self):
        camp_copy = copy(self.camp)
        camp_copy.colors.remove('pink_hex')

        assert not hasattr(camp_copy.colors, 'pink_hex')








