import pytest
from configmate.parsing import base_parser
from configmate.parsing import ini_parser
from configmate.parsing import json_parser
from configmate.parsing import toml_parser
from configmate.parsing import xml_parser
from configmate.parsing import yaml_parser


@pytest.mark.parametrize(
    "filepath, expected_parser",
    [
        ("file.ini", ini_parser.IniParser),
        ("file.json", json_parser.JsonParser),
        ("file.toml", toml_parser.TomlParser),
        ("file.xml", xml_parser.XmlParser),
        ("file.yaml", yaml_parser.YamlSafeLoadParser),
        ("file.yml", yaml_parser.YamlSafeLoadParser),
    ],
)
def test_infer_parser_from_filepath(filepath, expected_parser):
    result = base_parser.InferableConfigParser.infer_parser_from_filepath(filepath)
    assert result == expected_parser
