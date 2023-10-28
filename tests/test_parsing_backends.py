from typing import Callable
import pytest
from configmate import interface, parsing


def test_json_parser():
    data = interface.ConfigLike(
        """
    {
        "section1": {
            "option1": "value1",
            "option2": "value2"
        },
        "section2": {
            "option3": "value3",
            "option4": "value4"
        }
    }
    """
    )
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    result = parsing.parse_json(data)
    assert result == expected


def test_ini_parser():
    data = interface.ConfigLike(
        """
    [Section1]
    option1 = value1
    option2 = value2

    [Section2]
    option3 = value3
    option4 = value4
    """
    )
    expected = {
        "Section1": {"option1": "value1", "option2": "value2"},
        "Section2": {"option3": "value3", "option4": "value4"},
    }
    result = parsing.parse_ini(data)
    assert result == expected


def test_xml_parser():
    data = interface.ConfigLike(
        """
    <root>
        <section1>
            <option1>value1</option1>
            <option2>value2</option2>
            <section1.1>
                <option1.1.1>value1.1.1</option1.1.1>
                <option1.1.2>value1.1.2</option1.1.2>
            </section1.1>
        </section1>
        <section2>
            <option3>value3</option3>
            <option4>value4</option4>
        </section2>
    </root>
    """
    )
    expected = {
        "section1": {
            "option1": "value1",
            "option2": "value2",
            "section1.1": {
                "option1.1.1": "value1.1.1",
                "option1.1.2": "value1.1.2",
            },
        },
        "section2": {"option3": "value3", "option4": "value4"},
    }
    result = parsing.parse_xml(data)
    print(result)
    assert result == expected


### Optional parsers from extensions
def test_toml_parser():
    data = interface.ConfigLike(
        """
    [section1]
    option1 = "value1"
    option2 = "value2"

    [section2]
    option3 = "value3"
    option4 = "value4"
    """
    )
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    result = parsing.parse_toml(data)
    assert result == expected


def test_yaml_safe_load_parser():
    data = interface.ConfigLike(
        """
    section1:
        option1: value1
        option2: value2

    section2:
        option3: value3
        option4: value4
    """
    )
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    result = parsing.parse_yaml_safe(data)
    assert result == expected


@pytest.mark.parametrize(
    "filepath, expected_parser",
    [
        ("file.ini", parsing.parse_ini),
        ("file.INI", parsing.parse_ini),
        ("file.json", parsing.parse_json),
        ("file.toml", parsing.parse_toml),
        ("file.xml", parsing.parse_xml),
        ("file.yaml", parsing.parse_yaml_safe),
        ("file.yml", parsing.parse_yaml_safe),
    ],
)
def test_infer_parser_from_filepath(filepath: str, expected_parser: Callable) -> None:
    result = parsing.ParserRegistry.get_strategy(filepath)
    assert result == expected_parser
