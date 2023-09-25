import re
from typing import Dict
from unittest import mock

import pytest

from configmate import exceptions
from configmate.configuration import configuration_base, envvar_config_templates
from configmate.utils import envvar_utils


@pytest.mark.parametrize(
    "env, pattern, config_handling, input_str, expected",
    [
        (
            {"HOME": "/user/home"},
            re.compile(r"\$(\w+)"),
            configuration_base.EnvVarMode.IGNORE_MISSING,
            "$HOME is where i live",
            "/user/home is where i live",
        ),
        (
            {},
            re.compile(r"\$(\w+)"),
            configuration_base.EnvVarMode.IGNORE_MISSING,
            "$UNKNOWN to the unknown",
            "$UNKNOWN to the unknown",
        ),
        (
            {},
            re.compile(r"\$(\w+)"),
            configuration_base.EnvVarMode.FILL_WITH_BLANK,
            "$UNKNOWN to the unknown",
            " to the unknown",
        ),
        (
            {"USER_NAME": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.IGNORE_MISSING,
            "$USER_NAME is John",
            "John is John",
        ),
        (
            {"USER NAME": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.IGNORE_MISSING,
            "$USER NAME is John",
            "$USER NAME is John",
        ),
        (  # Commented out lines should not be replaced
            {"USER_NAME": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "#$USER_NAME is John",
            "#$USER_NAME is John",
        ),
        (  # Commented out lines should not be replaced
            {"USER_NAME": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "bla bla bla # $USER_NAME is John",
            "bla bla bla # $USER_NAME is John",
        ),
        (  # Before comment should be replaced
            {"USER_NAME": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "$USER_NAME # is John",
            "John # is John",
        ),
        (  # Commented out lines should not be replaced if its with //
            {"USER_NAME": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "// $USER_NAME is John",
            "// $USER_NAME is John",
        ),
        (
            {"COMPUTERNAME": "MyPC"},
            envvar_config_templates.WINDOWS_ENV_PATTERN,
            configuration_base.EnvVarMode.IGNORE_MISSING,
            "%COMPUTERNAME% is MyPC",
            "MyPC is MyPC",
        ),
        (
            {"COMPUTER NAME": "Batman"},
            envvar_config_templates.WINDOWS_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "%COMPUTER NAME%",
            "%COMPUTER NAME%",
        ),
    ],
)
def test_replace_env_variables(
    env: Dict[str, str],
    pattern: re.Pattern[str],
    config_handling: configuration_base.EnvVarMode,
    input_str: str,
    expected: str,
) -> None:
    with mock.patch.dict("os.environ", env, clear=True):
        config = configuration_base.EnvironmentVariableHandlingConfig(
            env_var_pattern=pattern,
            defaults={},
            handling=config_handling,
        )
        assert envvar_utils.replace_env_variables(input_str, config) == expected


@pytest.mark.parametrize(
    "env, pattern, config_handling, input_str",
    [
        (
            None,
            re.compile(r"\$(\w+)"),
            configuration_base.EnvVarMode.RAISE_MISSING,
            "$UNKNOWN",
        ),
        (
            {"USER": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "$USER_NAME",
        ),
        (
            {"COMPUTERNAME": "MyPC"},
            envvar_config_templates.WINDOWS_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "%USERNAME%",
        ),
    ],
)
def test_replace_env_variables_error_cases(
    env: Dict[str, str],
    pattern: re.Pattern[str],
    config_handling: configuration_base.EnvVarMode,
    input_str: str,
) -> None:
    with mock.patch.dict("os.environ", env or {}):
        config = configuration_base.EnvironmentVariableHandlingConfig(
            env_var_pattern=pattern,
            defaults={},
            handling=config_handling,
        )
        with pytest.raises(exceptions.UnfilledEnvironmentVariableError):
            envvar_utils.replace_env_variables(input_str, config)
