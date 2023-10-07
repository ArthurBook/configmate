import pytest

from configmate import parsing_backends


@pytest.mark.parametrize(
    "filepath, expected_parser",
    [
        ("file.ini", parsing_backends.IniParser),
        ("file.json", parsing_backends.JsonParser),
        ("file.toml", parsing_backends.TomlParser),
        ("file.xml", parsing_backends.XmlParser),
        ("file.yaml", parsing_backends.YamlSafeLoadParser),
        ("file.yml", parsing_backends.YamlSafeLoadParser),
    ],
)
def test_infer_parser_from_filepath(filepath, expected_parser):
    result = parsing_backends.FileParserRegistry.from_path(filepath)
    assert result == expected_parser
