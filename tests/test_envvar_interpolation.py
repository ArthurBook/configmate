import re
from typing import Dict
from unittest import mock

import pytest

from configmate import exceptions
from configmate.configuration import envvar_config
from configmate.interpolation import env_interpolator


@pytest.mark.parametrize(
    "env, pattern, config_handling, input_str, expected",
    [
        (
            {"HOME": "/user/home"},
            re.compile(r"\$(\w+)"),
            envvar_config.EnvVarMode.IGNORE_MISSING,
            "$HOME is where i live",
            "/user/home is where i live",
        ),
        (
            {},
            re.compile(r"\$(\w+)"),
            envvar_config.EnvVarMode.IGNORE_MISSING,
            "$UNKNOWN to the unknown",
            "$UNKNOWN to the unknown",
        ),
        (
            {},
            re.compile(r"\$(\w+)"),
            envvar_config.EnvVarMode.FILL_WITH_BLANK,
            "$UNKNOWN to the unknown",
            " to the unknown",
        ),
        (
            {"USER_NAME": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.IGNORE_MISSING,
            "$USER_NAME is John",
            "John is John",
        ),
        (
            {"$ ": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.IGNORE_MISSING,
            "100$ !!",
            "100$ !!",
        ),
        (
            {"$ ": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.IGNORE_MISSING,
            "100$ !!",
            "100$ !!",
        ),
        (
            {"USER NAME": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.IGNORE_MISSING,
            "$USER NAME is John",
            "$USER NAME is John",
        ),
        (  # Commented out lines should not be replaced
            {"USER_NAME": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.RAISE_MISSING,
            "#$USER_NAME is John",
            "#$USER_NAME is John",
        ),
        (  # Commented out lines should not be replaced
            {"USER_NAME": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.RAISE_MISSING,
            "bla bla bla # $USER_NAME is John",
            "bla bla bla # $USER_NAME is John",
        ),
        (  # Before comment should be replaced
            {"USER_NAME": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.RAISE_MISSING,
            "$USER_NAME # is John",
            "John # is John",
        ),
        (  # Commented out lines should not be replaced if its with //
            {"USER_NAME": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.RAISE_MISSING,
            "// $USER_NAME is John",
            "// $USER_NAME is John",
        ),
        (
            {"COMPUTERNAME": "MyPC"},
            envvar_config.WINDOWS_ENV_PATTERN,
            envvar_config.EnvVarMode.IGNORE_MISSING,
            "%COMPUTERNAME% is MyPC",
            "MyPC is MyPC",
        ),
        (
            {"COMPUTER NAME": "Batman"},
            envvar_config.WINDOWS_ENV_PATTERN,
            envvar_config.EnvVarMode.RAISE_MISSING,
            "%COMPUTER NAME%",
            "%COMPUTER NAME%",
        ),
    ],
)
def test_replace_env_variables(
    env: Dict[str, str],
    pattern: re.Pattern[str],
    config_handling: envvar_config.EnvVarMode,
    input_str: str,
    expected: str,
) -> None:
    with mock.patch.dict("os.environ", env, clear=True):
        config = envvar_config.EnvVarConfig(
            env_var_pattern=pattern,
            defaults={},
            handling=config_handling,
            ignore=[],
        )
        assert env_interpolator.fill_env_variables(input_str, config) == expected


@pytest.mark.parametrize(
    "env, pattern, config_handling, input_str",
    [
        (
            None,
            re.compile(r"\$(\w+)"),
            envvar_config.EnvVarMode.RAISE_MISSING,
            "$UNKNOWN",
        ),
        (
            {"USER": "John"},
            envvar_config.UNIX_ENV_PATTERN,
            envvar_config.EnvVarMode.RAISE_MISSING,
            "$USER_NAME",
        ),
        (
            {"COMPUTERNAME": "MyPC"},
            envvar_config.WINDOWS_ENV_PATTERN,
            envvar_config.EnvVarMode.RAISE_MISSING,
            "%USERNAME%",
        ),
    ],
)
def test_replace_env_variables_error_cases(
    env: Dict[str, str],
    pattern: re.Pattern[str],
    config_handling: envvar_config.EnvVarMode,
    input_str: str,
) -> None:
    with mock.patch.dict("os.environ", env or {}):
        config = envvar_config.EnvVarConfig(
            env_var_pattern=pattern,
            defaults={},
            handling=config_handling,
            ignore=[],
        )
        with pytest.raises(exceptions.UnfilledEnvironmentVariableError):
            env_interpolator.fill_env_variables(input_str, config)
