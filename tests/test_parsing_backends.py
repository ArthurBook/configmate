from configparser import ConfigParser
import contextlib
import copy
import importlib
import sys
from types import ModuleType
from typing import Callable
from unittest import mock

import pytest
from configmate import exceptions

from configmate.parsing import (
    base_parser,
    ini_parser,
    json_parser,
    toml_parser,
    xml_parser,
    yaml_parser,
)


def test_json_parser():
    data = """
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
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = json_parser.JsonParser()
    result = parser.parse(data)
    assert result == expected


def test_ini_parser():
    data = """
    [Section1]
    option1 = value1
    option2 = value2

    [Section2]
    option3 = value3
    option4 = value4
    """
    expected = {
        "Section1": {"option1": "value1", "option2": "value2"},
        "Section2": {"option3": "value3", "option4": "value4"},
    }
    configparser = ConfigParser()
    parser = ini_parser.IniParser(configparser)
    result = parser.parse(data)
    assert result == expected


def test_xml_parser():
    data = """
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
    parser = xml_parser.XmlParser()
    result = parser.parse(data)
    print(result)
    assert result == expected


### Optional parsers from extensions


@contextlib.contextmanager
def run_with_removed_module(dependency: str, module: ModuleType):
    try:
        with mock.patch.dict("sys.modules", {dependency: None}):
            importlib.reload(module)
            yield
    finally:  # Restore the state of the module
        importlib.reload(module)


@pytest.mark.parametrize(
    "dependency, module, parser_init",
    [
        ("toml", toml_parser, toml_parser.TomlParser),
        ("yaml", yaml_parser, yaml_parser.YamlSafeLoadParser),
        ("yaml", yaml_parser, yaml_parser.YamlUnSafeLoadParser),
    ],
)
def test_missing_imports(
    dependency: str,
    module: ModuleType,
    parser_init: Callable[[], base_parser.BaseConfigParser],
):
    with run_with_removed_module(dependency, module):
        with pytest.raises(exceptions.NeedsExtension):
            parser_init()


def test_toml_parser():
    data = """
    [section1]
    option1 = "value1"
    option2 = "value2"

    [section2]
    option3 = "value3"
    option4 = "value4"
    """
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = toml_parser.TomlParser()
    result = parser.parse(data)
    assert result == expected


def test_yaml_safe_load_parser():
    data = """
    section1:
        option1: value1
        option2: value2

    section2:
        option3: value3
        option4: value4
    """
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = yaml_parser.YamlSafeLoadParser()
    result = parser.parse(data)
    assert result == expected


def test_yaml_unsafe_load_parser():
    data = """
    section1:
        option1: value1
        option2: value2

    section2:
        option3: value3
        option4: value4
    """
    expected = {
        "section1": {"option1": "value1", "option2": "value2"},
        "section2": {"option3": "value3", "option4": "value4"},
    }
    parser = yaml_parser.YamlUnSafeLoadParser()
    result = parser.parse(data)
    assert result == expected
