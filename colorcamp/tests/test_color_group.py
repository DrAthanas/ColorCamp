import pytest
from conftest import param_color_spaces

from colorcamp.color_space import HSL, RGB, BaseColor, Hex
from colorcamp.groups import Map, Palette, Scale


@pytest.fixture(scope="class")
def cls_group(request):
    sky_hex: BaseColor = request.getfixturevalue("sky_Color").to_hex()
    pink_hex: BaseColor = request.getfixturevalue("pink_hex")
    mustard_hex: BaseColor = request.getfixturevalue("mustard_rgb").to_hex()
    lime_hex: BaseColor = request.getfixturevalue("lime_hsl").to_hex()

    request.cls.pal = Palette(
        colors=[sky_hex, pink_hex, mustard_hex, lime_hex],
        name="example",
        description="A beautiful color scale",
        metadata={"continuous ": "four color stops"},
    )


@pytest.mark.usefixtures("cls_group")
class TestScale:
    """test color group"""

    @pytest.mark.parametrize(
        ["group_type", "kw_args"],
        [
            ("Map", {}),
            ("Map", {"names": [0, 1, 2, 3]}),
            pytest.param("Map", {"names": [0, 1, 2]}, marks=pytest.mark.xfail(raises=ValueError)),
            ("Scale", {}),
            ("Scale", {"stops": [0, 0.2, 0.8, 1]}),
            ("Palette", {}),
        ],
    )
    def test_to_different_group(self, group_type: str, kw_args):
        assert isinstance(getattr(self.pal, f"to_{group_type.lower()}")(**kw_args), eval(group_type))

    @param_color_spaces
    def test_cast_color_space(self, color_space):
        new_pal = self.pal.to_color_space(color_space)

        assert all((isinstance(color, eval(color_space)) for color in new_pal))

    @pytest.mark.parametrize(
        ["group_type", "kw_args"],
        [
            ("Map", {}),
            ("Scale", {}),
            ("Palette", {}),
        ],
    )
    def test_to_native(self, group_type: str, kw_args):
        group = getattr(self.pal, f"to_{group_type.lower()}")(**kw_args)

        assert group.to_native()
