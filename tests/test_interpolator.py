import os
import pytest
from typing import Dict, Any, Type
from unittest import mock

from configmate.components import interpolators
from configmate.core import functions
from configmate.base import exceptions

TEST_FILE_FOLDER = "tests/test_files/"
FILE = "test_missing.json"


@pytest.mark.parametrize(
    "file, env, missing_handling_str, target",
    [
        (
            os.path.join(TEST_FILE_FOLDER, FILE),
            {"BAN": "ban"},
            "error",
            {"hax": "ban"},
        ),
    ],
)
def test_config_equals_expected(
    file: str, env: Dict[str, str], missing_handling_str: str, target: Dict[str, Any]
) -> None:
    """Asserts that the configuration is correctly parsed and equals the expected target."""
    with mock.patch.dict(os.environ, env, clear=True):
        config = functions.get_config(file, interpolation=missing_handling_str)
        assert config == target, f"Expected {target}, got {config}"


@pytest.mark.parametrize(
    "file, env, spec, exception",
    [
        (
            os.path.join(TEST_FILE_FOLDER, FILE),
            {},
            {},  # error is default
            exceptions.MissingEnvironmentVariable,
        ),
        (
            os.path.join(TEST_FILE_FOLDER, FILE),
            {},
            "error",
            exceptions.MissingEnvironmentVariable,
        ),
    ],
)
def test_correct_exception_raised(
    file: str,
    env: Dict[str, str],
    spec: interpolators.InterpolatorSpec,
    exception: Type[Exception],
) -> None:
    """Checks if the correct exception is raised when an environment variable is missing."""
    with mock.patch.dict(os.environ, env, clear=True), pytest.raises(exception):
        functions.get_config(file, interpolation=spec)


@pytest.mark.parametrize(
    "file, env, missing_handling_str",
    [
        (os.path.join(TEST_FILE_FOLDER, FILE), {}, "warn"),
    ],
)
def test_warning_raised(
    file: str, env: Dict[str, str], missing_handling_str: str
) -> None:
    """Verifies that a warning is raised under specific conditions."""
    with mock.patch.dict(os.environ, env, clear=True), pytest.warns(Warning):
        functions.get_config(file, interpolation=missing_handling_str)
