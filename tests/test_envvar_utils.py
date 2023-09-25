import os
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
            "$HOME is home",
            "/user/home is home",
        ),
        (
            None,
            re.compile(r"\$(\w+)"),
            configuration_base.EnvVarMode.IGNORE_MISSING,
            "$UNKNOWN is unknown",
            "$UNKNOWN is unknown",
        ),
        (
            None,
            re.compile(r"\$(\w+)"),
            configuration_base.EnvVarMode.FILL_WITH_BLANK,
            "$UNKNOWN is unknown",
            " is unknown",
        ),
        (
            {"USER_NAME": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.IGNORE_MISSING,
            "$USER_NAME is John",
            "John is John",
        ),
        (
            {"USER_NAME": "John"},
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "#$USER_NAME is John",  # Commented out lines should not be replaced
            "#$USER_NAME is John",
        ),
        (
            {"COMPUTERNAME": "MyPC"},
            envvar_config_templates.WINDOWS_ENV_PATTERN,
            configuration_base.EnvVarMode.IGNORE_MISSING,
            "%COMPUTERNAME% is MyPC",
            "MyPC is MyPC",
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
    with mock.patch.dict("os.environ", env or {}):
        config = configuration_base.EnvironmentVariableHandlingConfig(
            env_var_pattern=pattern,
            defaults={},
            handling=config_handling,
        )
        if (
            config_handling is configuration_base.EnvVarMode.RAISE_MISSING
            and env is None
        ):
            with pytest.raises(exceptions.UnfilledEnvironmentVariableError):
                envvar_utils.replace_env_variables(input_str, config)
        else:
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
            None,
            envvar_config_templates.UNIX_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "$USER_NAME",
        ),
        (
            None,
            envvar_config_templates.WINDOWS_ENV_PATTERN,
            configuration_base.EnvVarMode.RAISE_MISSING,
            "%COMPUTERNAME%",
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
