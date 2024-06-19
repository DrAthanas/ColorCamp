from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from bs4 import BeautifulSoup
from pytest import mark, param

from colorcamp._camp import Camp
from colorcamp._report import camp_to_html, report
from colorcamp._settings import settings
from colorcamp.color_space import BaseColor, Hex
from colorcamp.groups import Map, Palette, Scale


@pytest.fixture(scope="class")
def cls_camp(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: BaseColor = request.getfixturevalue("pink_hex")
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()
    pal = Palette((sky_hex, pink_hex, mustard_hex, lime_hex), name="Pal")

    camp = Camp(
        name="TestCamp",
        description="A group of colors and color objects",
        metadata={"version": "0.1.0"},
    )

    camp.add_objects(
        [
            sky_hex,
            pink_hex,
            mustard_hex,
            lime_hex,
            pal,
            Scale(pal, name="lette"),
            Map({"mustard": mustard_hex, "lime": lime_hex}, name="GoodFood"),
        ]
    )

    request.cls.camp: Camp = camp


@pytest.mark.usefixtures("cls_camp")
class TestCamp:
    """testing Camp"""

    def test_save_and_load(self):
        camp: Camp = self.camp

        with TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)

            camp.save(tempdir)

            new_camp = camp.load("TestCamp", tempdir)

            assert new_camp.colors.pink_hex == camp.colors.pink_hex
            assert new_camp.palettes.Pal == camp.palettes.Pal
            assert new_camp.scales.lette == camp.scales.lette

            with pytest.raises(FileExistsError):
                camp._description = "blah blah blah"
                camp.save(tempdir)

            with pytest.raises(FileExistsError):
                new_camp.colors.remove("pink_hex")
                new_camp.colors.add(Hex("#FFFFFF", name="pink_hex"))
                new_camp.save(tempdir)

    def test_names(self):
        assert len(self.camp.colors.names) == (len(self.camp.colors.__dict__) - 1)

    def test_no_name(self):
        with pytest.raises(AttributeError):
            self.camp.colors.add(Hex("#66FF66"))

    def test_name_in_use(self):
        with pytest.raises(ValueError):
            self.camp.colors.add(Hex("#66FF66", name="pink_hex"))

    def test_remove_color_object(self):
        camp_copy = deepcopy(self.camp)
        camp_copy.colors.remove("pink_hex")

        # Test we can't remove it again
        with pytest.raises(KeyError):
            camp_copy.colors.remove("pink_hex")

        assert not hasattr(camp_copy.colors, "pink_hex")

    def test_bucket_add_non_color_object(self):
        with pytest.raises(AttributeError):
            self.camp.colors.add("random")

    def test_bucket_wrong_color_object(self):
        with pytest.raises(TypeError):
            self.camp.colors.add(Palette((Hex("#000"), Hex("#FFF")), name="pal"))

    def test_incorrect_direct_assignment(self):
        with pytest.raises(AttributeError):
            nothing = Hex("#000", name="nothing")
            self.camp.colors.Something = nothing

    def test_equivalent_retrieval(self):
        assert self.camp.colors.sky_Color is self.camp.colors["sky_Color"]

    def test_adding_extra_redundant_items(self):
        camp_copy = deepcopy(self.camp)
        camp_copy.add_objects([Hex("#000", name="a"), Hex("#000", name="a")], exists_ok=True)

        with pytest.raises(ValueError):
            camp_copy.add_objects([Hex("#000", name="a")])

    @pytest.mark.parametrize(
        ("color_space"),
        [
            None,
            (("HSL", "Hex")),
            (["RGB"]),
            param(("XYZ"), marks=mark.xfail(ValueError, reason="Not supported color space")),
        ],
    )
    @pytest.mark.parametrize(
        ("sections"),
        [
            None,
            (("colors", "maps")),
            (("palettes", "colors")),
            param(("gaggle"), marks=mark.xfail(ValueError, reason="Not valid section")),
        ],
    )
    def test_html_report(self, color_space, sections):
        html_report = camp_to_html(
            self.camp,
            color_spaces=color_space,
            sections=sections,
        )

        assert bool(BeautifulSoup(html_report, "html.parser").find())

    def test_report(self, tmp_path):
        camp: Camp = self.camp

        assert report(camp) is None


@pytest.mark.parametrize(
    ("camp_name"),
    [
        ("web_colors"),
        ("carto"),
        ("colorbrewer"),
        ("seaborn"),
        ("crayons"),
        # ('XKCD'),
        # ('plotly'),
        param("web_colors2", marks=mark.xfail(FileNotFoundError, reason="No named color camp")),
    ],
)
def test_load_predefined_camps(camp_name):
    assert Camp.load(camp_name)


@pytest.mark.parametrize(
    ("directory", "exp1", "exp2"),
    [
        (None, len(settings.camp_paths), 5),
        (Path().cwd(), 1, 0),
    ],
)
def test_find_predefined_camps(directory, exp1, exp2):
    found_camps = Camp.find(directory)
    camp_names = []
    for _, names in found_camps.items():
        camp_names.extend(names)

    # length should be the same as the number of default paths
    assert len(found_camps) == exp1
    assert len(camp_names) == exp2
