import re
from typing import Dict
from unittest import mock

import pytest

from configmate import exceptions
from configmate import env_interpolator


@pytest.mark.parametrize(
    "env, pattern, config_handling, input_str, expected",
    [
        (
            {"HOME": "/user/home"},
            re.compile(r"\$(\w+)"),
            env_interpolator.MissingEnvVarHandling.IGNORE,
            "$HOME is where i live",
            "/user/home is where i live",
        ),
        (
            {},
            re.compile(r"\$(\w+)"),
            env_interpolator.MissingEnvVarHandling.IGNORE,
            "$UNKNOWN to the unknown",
            "$UNKNOWN to the unknown",
        ),
        (
            {"USER_NAME": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.IGNORE,
            "$USER_NAME is John",
            "John is John",
        ),
        (
            {"$ ": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.IGNORE,
            "100$ !!",
            "100$ !!",
        ),
        (
            {"$ ": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.IGNORE,
            "100$ !!",
            "100$ !!",
        ),
        (
            {"USER NAME": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.IGNORE,
            "$USER NAME is John",
            "$USER NAME is John",
        ),
        (  # Commented out lines should not be replaced
            {"USER_NAME": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.RAISE_EXCEPTION,
            "#$USER_NAME is John",
            "#$USER_NAME is John",
        ),
        (  # Commented out lines should not be replaced
            {"USER_NAME": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.RAISE_EXCEPTION,
            "bla bla bla # $USER_NAME is John",
            "bla bla bla # $USER_NAME is John",
        ),
        (  # Before comment should be replaced
            {"USER_NAME": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.RAISE_EXCEPTION,
            "$USER_NAME # is John",
            "John # is John",
        ),
        (  # Commented out lines should not be replaced if its with //
            {"USER_NAME": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.RAISE_EXCEPTION,
            "// $USER_NAME is John",
            "// $USER_NAME is John",
        ),
        (
            {"COMPUTERNAME": "MyPC"},
            env_interpolator.WINDOWS_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.IGNORE,
            "%COMPUTERNAME% is MyPC",
            "MyPC is MyPC",
        ),
        (
            {"COMPUTER NAME": "Batman"},
            env_interpolator.WINDOWS_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.RAISE_EXCEPTION,
            "%COMPUTER NAME%",
            "%COMPUTER NAME%",
        ),
    ],
)
def test_replace_env_variables(
    env: Dict[str, str],
    pattern: re.Pattern,
    config_handling: env_interpolator.MissingEnvVarHandling,
    input_str: str,
    expected: str,
) -> None:
    with mock.patch.dict("os.environ", env, clear=True):
        assert (
            env_interpolator.expand_env_vars(input_str, pattern, config_handling)
            == expected
        )


@pytest.mark.parametrize(
    "env, pattern, config_handling, input_str",
    [
        (
            None,
            re.compile(r"\$(\w+)"),
            env_interpolator.MissingEnvVarHandling.RAISE_EXCEPTION,
            "$UNKNOWN",
        ),
        (
            {"USER": "John"},
            env_interpolator.UNIX_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.RAISE_EXCEPTION,
            "$USER_NAME",
        ),
        (
            {"COMPUTERNAME": "MyPC"},
            env_interpolator.WINDOWS_ENV_PATTERN,
            env_interpolator.MissingEnvVarHandling.RAISE_EXCEPTION,
            "%USERNAME%",
        ),
    ],
)
def test_replace_env_variables_error_cases(
    env: Dict[str, str],
    pattern: re.Pattern,
    config_handling: env_interpolator.MissingEnvVarHandling,
    input_str: str,
) -> None:
    with mock.patch.dict("os.environ", env or {}):
        with pytest.raises(exceptions.UnfilledEnvironmentVariableError):
            env_interpolator.expand_env_vars(input_str, pattern, config_handling)
