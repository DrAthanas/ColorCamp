import pytest

from colorcamp.conversions import hex_to_rgb, rgb_to_hex, rgb_to_hsl


# ? Add expected failure cases
@pytest.mark.parametrize(
    "hex_string,rgb_tuple",
    [
        ("#000000", (0, 0, 0)),
        ("#FFFFFF", (255, 255, 255)),
        ("#000", (0, 0, 0)),
        ("#FFF", (255, 255, 255)),
        ("#7F7F7F", (127, 127, 127)),
        ("#7F7F7F7F", (127, 127, 127, 127 / 255)),
        ("#8888", (136, 136, 136, 136 / 255)),
    ],
)
def test_hex_to_rgb(hex_string, rgb_tuple):
    assert hex_to_rgb(hex_string) == rgb_tuple


# fmt: off
@pytest.mark.parametrize(
    "rgb_tuple,hex_string",
    [
        ((0, 0, 0),"#000000"),
        ((255, 255, 255), "#FFFFFF"),
        ((127, 127, 127), "#7F7F7F"),
        ((127, 127, 127, 127 / 255), "#7F7F7F7F"),
        ((136, 136, 136, 136 / 255), "#88888888"),
    ],
) # fmt: on
def test_rgb_to_hex(rgb_tuple, hex_string):
    assert rgb_to_hex(rgb_tuple) == hex_string


@pytest.mark.parametrize(
    'rgb_tuple,hsl_tuple',
    [   
        # Ghost White
        ((248/255,248/255,255/255),(240,1,0.9863))
    ]
)
def test_rgb_to_hsl(rgb_tuple, hsl_tuple):
    assert [round(val,4) for val in rgb_to_hsl(rgb_tuple)] == list(hsl_tuple)
