import pytest
from colorcamp import WebColor, Hex, RGB, HSL

# Standard test:
# python -m pytest colorcamp/tests/
# Test w/ coverage:
# python -m pytest --cov=colorcamp colorcamp/tests/

@pytest.fixture(scope="session")
def sky_webcolor():
    sky = WebColor(
        red=15/255, 
        green=182/255, 
        blue=255/255, 
        name="sky_webcolor",
        description="A nice pretty blue",
        metadata={'sentiment':'calm'}
    )

    return sky

@pytest.fixture(scope="class")
def cls_sky_webcolor(request):
    request.cls.color : WebColor = request.getfixturevalue('sky_webcolor')

@pytest.fixture(scope="session")
def pink_hex():
    pink = Hex(
        "#FF15AA", 
        name="pink_hex",
        description="An energizing pink",
        metadata={'sentiment':'excited'}
    )

    return pink

@pytest.fixture(scope="class")
def cls_pink_hex(request):
    request.cls.color : WebColor = request.getfixturevalue('pink_hex')

@pytest.fixture(scope="session")
def mustard_rgb():
    mustard = RGB(
        (255, 170, 21),
        name="mustard_rgb",
        description="An alarming yellow",
        metadata={'sentiment':'cautious'}
    )

    return mustard

@pytest.fixture(scope="class")
def cls_mustard_rgb(request):
    request.cls.color : WebColor = request.getfixturevalue('mustard_rgb')

@pytest.fixture(scope="session")
def lime_hsl():
    lime = HSL(
        (158.2051282051282, 0.9999999999999999, 0.5411764705882353), 
        name="lime_hsl",
        description="limes and avocado!",
        metadata={'sentiment':'healthy'}
    )

    return lime

@pytest.fixture(scope="class")
def cls_lime_hsl(request):
    request.cls.color : WebColor = request.getfixturevalue('lime_hsl')