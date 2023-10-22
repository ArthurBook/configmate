import pytest

from configmate import parsing


@pytest.mark.parametrize(
    "filepath, expected_parser",
    [
        ("file.ini", parsing.parse_ini),
        ("file.json", parsing.parse_json),
        ("file.toml", parsing.parse_toml),
        ("file.xml", parsing.parse_xml),
        ("file.yaml", parsing.parse_yaml_safe),
        ("file.yml", parsing.parse_yaml_safe),
    ],
)
def test_infer_parser_from_filepath(filepath, expected_parser):
    result = parsing.FileParserRegistry.from_path(filepath)
    assert result == expected_parser
