from functools import partial

import pytest

from colorcamp import settings
from colorcamp.color_space import HSL, RGB, BaseColor, Hex
from colorcamp.common.exceptions import NumericIntervalError

# Standard test:
# python -m pytest colorcamp/tests/
# Test w/ coverage:
# python -m pytest --cov=colorcamp colorcamp/tests/

settings.max_precision = 6


@pytest.fixture(scope="session")
def sky_Color():
    sky = BaseColor(
        red=15 / 255,
        green=182 / 255,
        blue=255 / 255,
        name="sky_Color",
        description="A nice pretty blue",
        metadata={"sentiment": "calm"},
    )

    return sky


@pytest.fixture(scope="class")
def cls_sky_Color(request):
    request.cls.color: BaseColor = request.getfixturevalue("sky_Color")


@pytest.fixture(scope="session")
def pink_hex():
    pink = Hex(
        "#FF15AA",
        name="pink_hex",
        description="An energizing pink",
        metadata={"sentiment": "excited"},
    )

    return pink


@pytest.fixture(scope="class")
def cls_pink_hex(request):
    request.cls.color: BaseColor = request.getfixturevalue("pink_hex")


@pytest.fixture(scope="session")
def mustard_rgb():
    mustard = RGB(
        (255, 170, 21),
        name="mustard_rgb",
        description="An alarming yellow",
        metadata={"sentiment": "cautious"},
    )

    return mustard


@pytest.fixture(scope="class")
def cls_mustard_rgb(request):
    request.cls.color: BaseColor = request.getfixturevalue("mustard_rgb")


@pytest.fixture(scope="session")
def lime_hsl():
    lime = HSL(
        (158.2051282051282, 1, 0.5411764705882353),
        name="lime_hsl",
        description="limes and avocado!",
        metadata={"sentiment": "healthy"},
    )

    return lime


@pytest.fixture(scope="class")
def cls_lime_hsl(request):
    request.cls.color: BaseColor = request.getfixturevalue("lime_hsl")


#####################
### common params ###
#####################

param_color_init = partial(
    pytest.mark.parametrize(
        "params",
        [
            {"red": 0, "green": 1, "blue": 1.2},
            {"red": 0, "green": 1, "blue": -1},
            {"red": 0, "green": -1, "blue": 0.5},
            {"red": 255, "green": 0.3, "blue": 0.4},
            {"red": 0, "green": 1, "blue": 0.2, "alpha": -0.1},
            {"red": 0, "green": 1, "blue": 0.2, "alpha": 1.1},
        ],
    )
)

param_colors = partial(
    pytest.mark.parametrize(
        "color",
        [
            ("sky_Color"),
            ("pink_hex"),
            ("mustard_rgb"),
            ("lime_hsl"),
        ],
    )
)

param_color_spaces = partial(
    pytest.mark.parametrize(
        "color_space",
        [
            "BaseColor",
            "Hex",
            "RGB",
            "HSL",
        ],
    )
)

param_hex_codes = partial(
    pytest.mark.parametrize(
        "hex_code",
        [
            "#000000",
            "#000",
            "#FFFFFFFF",
            "#ffff",
            "#1a5500",
            pytest.param(
                "000",
                marks=pytest.mark.xfail(ValueError, reason="Doesn't start with #"),
            ),
            pytest.param("#GGggGG", marks=pytest.mark.xfail(ValueError, reason="Invalid hex")),
            pytest.param("#FF", marks=pytest.mark.xfail(ValueError, reason="Wrong length")),
        ],
    )
)

param_rgb_values = partial(
    pytest.mark.parametrize(
        "rgb",
        [
            (0, 255, 123),
            (0, 255, 123, 0.5),
            pytest.param(
                (-1, 255, 123),
                marks=pytest.mark.xfail(NumericIntervalError, reason="negative RGB values"),
            ),
            pytest.param(
                (0, 255, 256),
                marks=pytest.mark.xfail(NumericIntervalError, reason="above max RGB value"),
            ),
            pytest.param(
                (0, 255, 256, 1.1),
                marks=pytest.mark.xfail(NumericIntervalError, reason="above alpha value"),
            ),
        ],
    )
)

param_hsl_values = partial(
    pytest.mark.parametrize(
        "hsl",
        [
            (0, 0.8, 0.1),
            (360, 0, 1, 0.5),
            pytest.param(
                (361, 0.8, 0.1),
                marks=pytest.mark.xfail(NumericIntervalError, reason="above max hue value"),
            ),
            pytest.param(
                (360, -0.1, 1),
                marks=pytest.mark.xfail(NumericIntervalError, reason="below min saturation value"),
            ),
        ],
    )
)
