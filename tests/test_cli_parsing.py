import json
from typing import Any, Callable, Sequence
from unittest import mock

import pytest

from configmate import source_reading


# Test for FileSource
def test_filesource():
    src = source_reading.FileSource("test.txt", "utf-8")
    with mock.patch("pathlib.Path.read_text", return_value="mock_content"):
        assert src.read() == "mock_content"


# Test for SectionFinder
@pytest.mark.parametrize(
    "sectionfinder, cli_args, expected_output",
    [
        (
            source_reading.SectionFinder(
                section_start_finder=lambda x: x.startswith("Bla"),
                section_end_finder=lambda x: x == "/",
            ),
            ["Bla", "+section", "your_expected_output", "/", "raxban"],
            ["Bla", "+section", "your_expected_output", "/"],
        ),
        (
            source_reading.SectionFinder(
                section_start_finder=lambda x: x.startswith("Burp"),
                section_end_finder=lambda x: x == "/",
            ),
            ["Bla", "Bla", "Burp", "rax", "/"],
            ["Burp", "rax", "/"],
        ),
        (
            source_reading.SectionFinder(
                section_start_finder=lambda x: x.startswith("Burp"),
                section_end_finder=lambda x: x == "/",
            ),
            ["Bla", "Bla", "Ding", "Dong", "/", "Burp", "rax", "/"],
            ["Burp", "rax", "/"],
        ),
        (
            source_reading.SectionFinder.from_tokens("Burp", "/"),
            ["Bla", "Bla", "Ding", "Dong", "/", "Burp", "rax", "/"],
            ["Burp", "rax", "/"],
        ),
        (
            source_reading.SectionFinder.from_tokens("Burp", "/"),
            ["Bla", "Bla", "Ding", "Dong", "/", "aBurp", "rax", "/"],
            [],
        ),
    ],
)
def test_sectionfinder(
    sectionfinder: source_reading.SectionFinder,
    cli_args: Sequence[str],
    expected_output: Any,
):
    with mock.patch("sys.argv", cli_args):
        assert list(sectionfinder) == expected_output


# Test for make_nested_dict
@pytest.mark.parametrize(
    "keys, value, expected_output",
    [
        (
            ["a", "b", "c"],
            1,
            {"a": {"b": {"c": 1}}},
        ),
    ],
)
def test_make_nested_dict(keys: Sequence[str], value: Any, expected_output: Any):
    assert source_reading.make_nested_dict(keys, value) == expected_output


@pytest.mark.parametrize(
    "overlay_parser, cli_args, expected_output",
    [
        (
            source_reading.OverlayParser.from_prefix_token("+"),
            ["+section", "your_expected_output", "+", "raxban"],
            ["section"],
        ),
        (
            source_reading.OverlayParser.from_prefix_token("+"),
            ["++section"],
            [],
        ),
        (
            source_reading.OverlayParser.from_prefix_token("-"),
            ["-section-1"],
            ["section-1"],
        ),
        (
            source_reading.OverlayParser.from_prefix_token("+"),
            ["+section-1", "+section-2"],
            ["section-1", "section-2"],
        ),
    ],
)
def test_overlay_parser(
    overlay_parser: source_reading.OverlayParser,
    cli_args: Sequence[str],
    expected_output: Any,
) -> None:
    assert list(overlay_parser.parse(cli_args)) == expected_output


@pytest.mark.parametrize(
    "override_parser, cli_args, expected_output",
    [
        (
            source_reading.OverrideParser.from_tokens("+", ".", json.loads),
            ["+section", '"your_expected_output"'],
            [{"section": "your_expected_output"}],
        ),
        (
            source_reading.OverrideParser.from_tokens("+", ".", json.loads),
            ["+section.subsection", '"your_expected_output"'],
            [{"section": {"subsection": "your_expected_output"}}],
        ),
        (
            source_reading.OverrideParser.from_tokens("+", ".", json.loads),
            ["+section", "null"],
            [{"section": None}],
        ),
        (
            source_reading.OverrideParser.from_tokens("-", ".", json.loads),
            ["-section", "null"],
            [{"section": None}],
        ),
        (
            source_reading.OverrideParser.from_tokens("-", ".", json.loads),
            ["-section", '["ding","dong"]'],
            [{"section": ["ding", "dong"]}],
        ),
        (
            source_reading.OverrideParser.from_tokens("-", ".", json.loads),
            ["-section", '["ding","dong"]'],
            [{"section": ["ding", "dong"]}],
        ),
        (
            source_reading.OverrideParser.from_tokens("+", ".", json.loads),
            ["+section", '{"rax": "ban", "sax": null}'],
            [{"section": {"rax": "ban", "sax": None}}],
        ),
    ],
)
def test_override_parser(
    override_parser: source_reading.OverrideParser,
    cli_args: Sequence[str],
    expected_output: Any,
) -> None:
    assert list(override_parser.parse(cli_args)) == expected_output
