from tempfile import NamedTemporaryFile

import pytest

from colorcamp._color_metadata import MetaColor
from colorcamp.color_space import BaseColor


@pytest.fixture(scope="class")
def color_metadata(request):
    cm = MetaColor(
        name="cyan_O00",
        description="This is just some plain text",
        metadata={"value": 123, "sub_desc": "blue"},
    )

    request.cls.color_metadata = cm


@pytest.mark.usefixtures("color_metadata")
class TestColorMetadata:
    def test_rename(self):
        with pytest.raises(AttributeError):
            self.color_metadata.name = "new_name"

    def test_re_description(self):
        with pytest.raises(AttributeError):
            self.color_metadata.description = "Ipsum lorem"

    def test_metadata(self):
        with pytest.raises(AttributeError):
            self.color_metadata.metadata = {"new_thing": 1234}

    def test_file_path_exists(self):
        self.color_metadata: MetaColor
        with NamedTemporaryFile() as tempfile:
            with pytest.raises(FileExistsError):
                self.color_metadata.dump_json(tempfile.name)


@pytest.mark.parametrize(
    ["new_info", "new_name"],
    [
        ({"name": "happy_new_name"}, "happy_new_name"),
        pytest.param({}, "", marks=pytest.mark.xfail(raises=ValueError)),
        pytest.param({"x": 123, "name": "happy_new_name"}, "", marks=pytest.mark.xfail(raises=ValueError)),
    ],
)
def test_change_info(new_info, new_name):
    bc = BaseColor(
        0.5,
        0.2,
        0.9,
        name="test_color",
        description="I love my dog",
        metadata={"value": 123, "sub_desc": "blue"},
    )

    assert bc.change_info(**new_info).name == new_name


### Fail Cases ###
# ? Move these to test_validators
@pytest.mark.parametrize(
    ["name", "exception"],
    [
        (".hidden_name", ValueError),
        (1234, TypeError),
        ("&a", ValueError),
        ("", ValueError),
        ("invalid-name", ValueError),
    ],
)
def test_bad_names(name, exception):
    with pytest.raises(exception):
        MetaColor(name=name, description="Failure")


@pytest.mark.parametrize(
    ["description", "exception"],
    [
        ("A" * 1000, ValueError),
        (1234, TypeError),
    ],
)
def test_bad_descriptions(description, exception):
    with pytest.raises(exception):
        MetaColor(name="name", description=description)
